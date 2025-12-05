import json
import asyncio
from pong.game import Game
from pong.data import setup_game_data, DEFAULT_DATA, seconds_to_refresh
from server.logging import logger
from server.asyncredis import redis

from .tools import all_players_connected, get_game_status, update_game_params, get_running_games, does_game_exist, clean_pending_games, move_game_to, register_tournament, is_running_tournament, is_running, get_game_param, unlock_for_creation, is_allowed_for_creation, lock_for_creation, create_new_game, create_new_single_game, create_new_tournament, get_all_games, lock_game, PENDING_TOURNAMENTS, get_running_tournaments, RUNNING_TOURNAMENTS, PENDING_GAMES, RUNNING_GAMES, PENDING, RUNNING
from .Tournament import Tournament, get_next_game, all_games_played, get_tournament_stats, debug_tree
from channels.generic.websocket import AsyncWebsocketConsumer

from django.contrib.auth import get_user_model
from .data import setup_game_data, setup_tournament_data
from datetime import datetime, timezone
from channels.layers import get_channel_layer
import uuid
from asgiref.sync import sync_to_async
from . import models

class PongGeneralConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"].username
        if self.scope["user"].is_authenticated:
            await self.accept()
        else:
            await self.close(code=4001)
            return

        self.room_name = "all_games"
        self.channel_layer = get_channel_layer()
        await self.channel_layer.group_add(f"user_{self.user}", self.channel_name)
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.send(text_data=json.dumps({"message": "connected to Pong Lobby, sending games...!"}))
        data = await get_all_games(self.user)
        if data :
            await self.send(text_data=json.dumps(data))
        else :
            await self.send(text_data=json.dumps({"message": "no available games"}))
        reco = await get_running_games(self.user)
        if reco:
            if reco["game_param"]["opponent"] == "remote":
                for user in reco["allowed_users"]:
                    try:
                        await self.channel_layer.group_send(
                            f"user_{user}",
                            {
                                **reco,
                                "type": "notify_user",
                                "status": "in_progress"
                            }
                        )
                    except Exception as e:
                        logger.error(f"❌ [GameConsumer] Error sending game notification: {e}")
        reco_data =  await get_running_tournaments(self.user)
        if reco_data:
            await self.reco_tournament(reco_data)

                
    async def disconnect(self, code):
        await self.channel_layer.group_discard(f"user_{self.user}", self.channel_name)
        # await unlock_for_creation(self.user)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")
        actions_map = {
            "new_game": self.announce_new_game,
            "join_game": self.join_game,
            "join_tournament": self.join_tournament,
            "new_ai_game": self.announce_new_game,
            "new_invited_game": self.announce_new_game,
            "new_tournament": self.announce_new_tournament,
            "canceled_tournament": self.cancel_tournament,
            "canceled_game": self.cancel_game,
        }

        perform = actions_map.get(action)
        if (perform):
            await perform(data)

    async def reco_tournament(self, data):
        logger.info(f"DEBUGGGGGG reco_tournament called")
        tournament_uid = data.get("tournament_uid")
        if not tournament_uid:
            logger.error(f"❌ [PongGeneralConsumer] Invalid tournament id - the tournament is over or timed out")        
            await self.notify("access_refused", "Invalid tournament id - the tournament is over or timed out", f"user_{self.user}", data)
            await self.close(1008)
            return
        status = await get_game_status(tournament_uid)
        logger.info(f"status is : {status}")
        data["type"] = "notify_user"
        if status == RUNNING:
            await self.notify("tournament_ready", "you will be redirected to the tournament", f"user_{self.user}", data)


    async def join_tournament(self, data):
        user = self.scope["user"].username
        tournament_uid = data.get("tournament_uid")
        if not tournament_uid:
            await self.notify("failed", "no id tournament_id found",f"user_{user}")
            return
        tournament = await get_game_param(tournament_uid)
        if user in tournament["players"]:
            await self.notify("already registered", "you are already resgistered",f"user_{user}")
            return
           
        notification = await register_tournament(user, tournament_uid)

        notification["game_param"] = tournament["game_param"]
        if notification:
            notification["new_player"] = user
            if notification.get("status") == "tournament_full":
                await self.notify_users(notification, "tournament_ready")
                await asyncio.sleep(0.1)
                await self.channel_layer.group_send(
                            self.room_name,
                            {"type": "send_game_announcement",
                            "status": "remove_tournament",                    
                            "game_uid": tournament_uid,
                            "message": "A Tournament has been locked"
                            }
                )
            else:
                notification["status"] = "join_tournament"
                await self.notify("join_tournament", f"{user} join the tournament", self.room_name, {**notification})
        else:
            await self.notify("register failed", "tournament is unavailable : locked or finished",f"user_{user}")


    async def join_game(self, data):
        user = self.scope["user"].username
        game_uid = data.get("game_uid")
        await clean_pending_games()
        if not game_uid:
            await self.notify("failed", "no id game_id found",f"user_{user}")
            return
        if not await does_game_exist(game_uid):
            await self.notify("failed", "Sorry, game_id no longer exists. Game request timed out", f"user_{user}")
            return            
        game = await lock_game(game_uid, self.scope["user"].username)
        if game["status"] == "ready":
            if game["game_param"]["opponent"] == "remote":
                await self.notify_users(game, "game_ready")
            await self.notify("remove_game", "remove_game", self.room_name, {"game_uid": game_uid})
        else:
            await self.error_message(game)


    async def error_message(self, game):
        user = self.scope["user"].username
        try:
            await self.channel_layer.group_send(
                f"user_{user}",
                {
                    "type": "notify_user",
                    "status": "game_error",
                    "game": game
                }
            )
        except Exception as e:
            logger.error(f"❌ [GameConsumer] Error sending game notification: {e}")


    async def notify_users(self, game, status):
        key = "allowed_users"
        if not key in game:
            key = "players"
        if not key in game:
            logger.error(f"❌ [GameConsumer] Error sending game notification: bad formed request")
        for user in game[key]:
            try:
                await self.channel_layer.group_send(
                    f"user_{user}",
                    {
                        **game,
                        "type": "notify_user",
                        "status": status
                    }
                )
            except Exception as e:
                logger.error(f"❌ [GameConsumer] Error sending game notification: {e}")

    async def notify(self, status, message, recipient, data={}):
            await self.channel_layer.group_send(recipient,
            {
                "type": "notify_user",
                "status": status,
                "message": message,
                **data
            })

    async def notify_user(self, event):
        game_uid = event.get("game_uid")
        game_param = event.get("game_param")
        if game_uid:
            event["game_uid"] = game_uid
        if game_param:
            event["removed"] = game_param
        try:
            await self.send(text_data=json.dumps({**event}))
        except Exception as e:
            logger.error(f"❌ [PongConsumer] Error sending game announcement: {e}")

    async def cancel_tournament(self, data):
        user = self.scope["user"].username
        if data:
            game_uid = data.get("game_uid")
            if game_uid:
                game_raw = await get_game_param(game_uid)
                if user == game_raw["created_by"]:
                    if not await is_running(game_uid, RUNNING_TOURNAMENTS):
                        await redis.srem(PENDING_TOURNAMENTS, game_uid)                  
                        await redis.delete(game_uid)                    
                        await unlock_for_creation(user)
                        await self.notify("tournament_deleted", "your tournament has been deleted", f"user_{user}")
                        await self.channel_layer.group_send(
                            self.room_name,
                            {
                                "type": "send_game_announcement",
                                "status": "tournament_deleted",                    
                                "action": "tournament_deleted",
                                "game_uid": game_uid,
                                "message": "A tournament has been deleted!"
                                }
                        )
                        return
                    else:
                        await self.notify("delete_error", "your game status is running. await end of the tournament or forfeit", f"user_{user}")
                else :
                    await self.notify("delete_error", "invalid delete request... your not the tournament creator", f"user_{user}")
                    return
            else : 
                await self.notify("delete_error", "invalid delete request... missing game_uid to complete operation", f"user_{user}")
                return
        else :    
            await self.notify("delete_error", "invalid delete request... missing data", f"user_{user}")
            return


    async def cancel_game(self, data):
        user = self.scope["user"].username
        if data:
            game_uid = data.get("game_uid")
            if game_uid:
                game_raw = await get_game_param(game_uid)
                if user == game_raw["created_by"]:
                    result = await is_running(game_uid, RUNNING_GAMES)
                    logger.info(f"cancel game - result : {result}") 
                    if await is_running(game_uid, RUNNING_GAMES):                    
                        await self.notify("delete_error", "your game status is running. await end of the game", f"user_{user}")
                        return
                    else:
                        await redis.delete(game_uid)
                        await redis.srem(PENDING_GAMES, game_uid)
                        await unlock_for_creation(user)
                        await self.notify("game_deleted", "your game has been deleted", f"user_{user}")
                        await self.channel_layer.group_send(
                            self.room_name,
                            {"type": "send_game_announcement",
                            "status": "game_deleted",                    
                            "action": "game_deleted",
                            "game_uid": game_uid,
                            "message": "A game has been deleted!"
                            }
                        )
                        return
                else:
                    await self.notify("delete_error", "invalid delete request... your not the game creator", f"user_{user}")
                    return
            else:
                await self.notify("delete_error", "invalid delete request... missing game_uid to complete operation", f"user_{user}")
                return
        else:
            await self.notify("delete_error", "invalid delete request... missing data", f"user_{user}")
            return

    async def setup_new_game(self, game_request, game_uid):
        user = self.scope["user"].username
        status = "pending"
        players = 1
        opponent = game_request["game_param"]["opponent"]
        if opponent != "remote":
            players = 2
            status = "ready"

        game_data = {
            "players": players,
            "from_tournament": False,
            "game_param" : game_request.get("game_param"),
            "status": status,
            "game_uid": game_uid,
            "from_tournament": False,
            "tournament_uid" : None,
            "type": game_request.get("action"),
            "created_by": user,
            "player1": user,
            "player2": "pending"}
        return game_data
        
    async def prepare_new_game_announcement(self, game_request, game_uid):        
        user = self.scope["user"].username
        user_address = f"user_{user}"
        receivers = self.room_name
        creation_status = "game_created"
        opponent = game_request["game_param"]["opponent"]
        game_response = {
            "type": "send_game_announcement",
            "status": creation_status,
            "action": game_request.get("action"),
            "from_tournament": False,
            "tournament_uid" : None,
            "game_uid": game_uid,
            "created_by": user,
            "player1" : user,
            "message": "A new game has been created!",
            "game_param" : game_request.get("game_param")
            }
        if opponent != "remote":
            game_response["allowed_users"] = [user]
            game_response["status"] = "game_ready"
            receivers = user_address
            game_response["left"] = game_request["left"]
            game_response["right"] = game_request["right"]
            game_response["player2"] = game_request["player2"]

        if self.channel_layer:
            try:
                await self.channel_layer.group_send(
                    receivers,
                    game_response
                )
            except Exception as e:
                logger.error(f"❌ [PongConsumer] Error sending game announcement: {e}")


    async def announce_new_game(self, game_request):
        user = self.scope["user"].username
        if await is_allowed_for_creation(user):
            await lock_for_creation(user)
            game_uid = str(uuid.uuid4())
            game_data = await self.setup_new_game(game_request, game_uid)
            opponent = game_request["game_param"]["opponent"]
            if opponent != "remote":
                prepared_game = await create_new_single_game(game_data, game_uid)
                await self.prepare_new_game_announcement(prepared_game, game_uid)
            else :
                await create_new_game(game_data, game_uid)
                await self.prepare_new_game_announcement(game_request, game_uid)
        else:
            await self.notify("failed", "you already created another game or tournament", f"user_{user}")

    async def announce_new_tournament(self, tournament_request):
        expected = tournament_request["game_param"].get("player")
        user = self.scope["user"].username
        if await is_allowed_for_creation(user):
            await lock_for_creation(user)
            tournament_uid = str(uuid.uuid4())
            tournament = {"joined": 1,
                          "expected": expected,
                          "players": [user], 
                        "status": "pending",
                        "game_param" : tournament_request.get("game_param"),
                        "tournament_uid": tournament_uid,
                        "type":tournament_request.get("action"),
                        "created_by": user}
            await create_new_tournament(tournament, tournament_uid)
            res = json.loads(await redis.get(tournament_uid))
            if self.channel_layer:
                try:
                    await self.channel_layer.group_send(
                        self.room_name,
                        {"type": "send_game_announcement",
                        "status": "tournament_created",                    
                        "action": tournament_request.get("action"),
                        "joined" : 1,
                        "expected": expected,
                        "tournament_uid": tournament_uid,
                        "game_param" : tournament_request.get("game_param"),
                        "created_by": user,
                        "message": "A new tournament has been created!"}
                    )
                except Exception as e:
                    logger.error(f"❌ [PongConsumer] Error sending game announcement: {e}")
        else:
            await self.notify("failed", "you already created another game or tournament", f"user_{user}")




    async def send_game_announcement(self, event):
        try:
            await self.send(text_data=json.dumps({**event}))
        except Exception as e:
            logger.error(f"❌ [PongConsumer] Error sending game announcement: {e}")
    

    async def acknoledge_connection(self, event):
        try:
            await self.send(text_data=json.dumps({"message":event["message"]}))
        except Exception as e:
            logger.error(f"❌ [PongConsumer] Error sending game state: {e}")


active_games = {}
active_tournaments = {}
active_monitors = {}


class PongConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.to_general = "all_games"
        self.channel_layer = get_channel_layer()
        self.game_uid = self.scope['url_route']['kwargs'].get('game_uid', None)
        self.CONNECTED = f"{self.game_uid}_connected"
        self.FIRSTCONNECTION = f"{self.game_uid}_firstconnection"
        self.user = self.scope["user"].username
        if not self.channel_layer:
            logger.warning("⚠️ [PongConsumer] Channel Layer is None, WebSocket will function in direct mode.")
            await self.close(code=4001)
            return
        if not self.game_uid:
            await self.close(code=4001)
            return
        is_ready = await redis.sismember(RUNNING_GAMES, self.game_uid)
        if (is_ready):
            game_params_raw = await redis.get(self.game_uid)
            if game_params_raw:
                game_params = json.loads(game_params_raw)

                game_params["status"] = "in_progress"
                game_params_raw = json.dumps(game_params)
                await redis.set(self.game_uid, game_params_raw)               
                self.opponent = game_params["game_param"]["opponent"]
                self.allowed_users = game_params["allowed_users"]
                self.opponent_name = None
                if len(self.allowed_users) > 1 :
                    self.opponent_name = self.allowed_users[1] if self.allowed_users[0] == self.user else self.allowed_users[0]
                if self.user not in self.allowed_users:
                    await self.close(4001)
                    return
                connected = await redis.sismember(self.CONNECTED, self.user)
                if connected:            
                    await self.close(code=4001)
                    await asyncio.sleep(0.05)    
                await redis.sadd(self.CONNECTED, self.user)
                try:
                    await self.channel_layer.group_add(self.game_uid, self.channel_name)
                    await self.channel_layer.group_add(f"game_user_{self.user}", self.channel_name)
                    logger.info(f"➕ {self.channel_name} in group game_user_{self.user}")
                    await asyncio.sleep(0.05)  
                    logger.info("🔗 [PongConsumer] Added to WebSocket group")
                except Exception as e:
                    logger.error(f"❌ [PongConsumer] Error adding to WebSocket group: {e}")
                await self.connected_message()
                await self.accept()
                logger.info("✅ [PongConsumer] Connection accepted")
            else:
                await self.close(code=4001)
                return
        else:
            logger.error(f"❌ [PongConsumer] Socket not ready")
            await self.close(code=4001)
            return

        logger.info("🖲️​ [PongConsumer] Initializing WebSocket...")
        lock_key = f"game_creation_lock_{self.game_uid}"
        
        if not await redis.sismember(self.FIRSTCONNECTION, self.user):
            await redis.sadd(self.FIRSTCONNECTION, self.user)
            if await redis.set(lock_key, 1, nx=True, ex=60):
                try:
                    if self.game_uid not in active_games:
                        self.data = await setup_game_data(self.game_uid)
                        game = Game(self.data)
                        await game.setup_game(self.data)
                        active_games[self.game_uid] = game
                finally:
                    await redis.delete(lock_key)
            else:
                while self.game_uid not in active_games:
                    await asyncio.sleep(0.05) 
            self.game = active_games[self.game_uid]
        else:
            self.game = active_games[self.game_uid]


        if await redis.get(f"{self.game_uid}_paused"):
            await self.notify("game_paused", "Game was paused due to disconnection. Waiting for all players to reconnect.", f"user_{self.user}")
            logger.info(f"⏸️ [PongConsumer] User {self.user} reconnected to paused game")
        if await redis.scard(self.CONNECTED) == 2:
            if await redis.get(f"{self.game_uid}_paused"):
                # await redis.delete(f"{self.game_uid}_paused")
                await self.notify("resume", "All players reconnected. You can resume the game.", self.game_uid)
                logger.info("✅ [PongConsumer] Game can be resumed - all players back")
            else:
                await self.notify("waiting", "waiting players ready notification", self.game_uid)
                if self.opponent != 'ia' and self.opponent != 'invited':
                    date = datetime.now(timezone.utc).isoformat()
                    await self.notify("game_info", "A new game is ready ! Please join the arena", f"room_{self.user}", {"date" : date})


    async def disconnect(self, close_code):
        logger.info(f"❌ [PongConsumer] {self.user} Disconnected from {self.game_uid} with code {close_code}")
        match_over = await self.game.is_match_over()
        if not match_over and self.game_uid in active_games:
            await redis.set(f"{self.game_uid}_paused", 1, ex=300)
        self.game.running = False
        await redis.srem(self.CONNECTED, self.user)
        status = "disconnect"
        if match_over:
            status = "leave"
        logger.info(f"OPPONENT IS : ------------------------------------------------------------------{self.opponent}")
        if self.opponent == "ai" or self.opponent == "invited":
            await unlock_for_creation(self.user)
            await self.cleanup()
        if self.opponent_name:
            if await redis.sismember(f"{self.game_uid}_ready", self.opponent_name):
                await self.notify(status, "your opponent left the game", f"user_{self.opponent_name}", data={"user":self.opponent_name})
        await self.notify(status, "you left the game", f"user_{self.user}", data={"user":self.user})
        await redis.delete(f"{self.game_uid}_ready")



    async def cleanup(self):
        active_games.pop(self.game_uid, None)
        await redis.delete(self.game_uid)
        await redis.delete(f"{self.game_uid}_connected")
        await redis.delete(self.FIRSTCONNECTION)
        await redis.delete(f"{self.game_uid}_ready")
        if await redis.sismember(RUNNING_GAMES, self.game_uid):
            await redis.srem(RUNNING_GAMES, self.game_uid)
        await self.channel_layer.group_discard(self.game_uid, self.channel_name)
        await unlock_for_creation(self.user)
        if self.opponent_name:
            await unlock_for_creation(self.opponent_name)


    async def connected_message(self):
            try:
                await self.channel_layer.group_send(
                f"user_{self.user}",
                    {"type": "acknoledge_connection", "message": "connected to game socket"}
                )
            except Exception as e:
                logger.error(f"❌ [PongConsumer] Error sending to Redis: {e}")

    async def notify(self, status, message, recipient, data={}):
            await self.channel_layer.group_send(recipient,
            {
                "type": "notify_user",
                "status": status,
                "message": message,
                "game_uid": self.game_uid,
                **data
            })

    async def notify_user(self, event):
            try:
                await self.send(text_data=json.dumps({**event}))
            except Exception as e:
                logger.error(f"❌ [PongConsumer] Error sending game announcement: {e}")

    async def check_ready(self):
            user = self.scope["user"].username
            if self.opponent == "ai" or self.opponent =="invited":
                await self.notify("start_game", "ready to play", f"user_{user}")
                return True
            res = await redis.sadd(f"{self.game_uid}_ready", user)
            if res == 0:
                logger.info(f"player already send ready status")
            if await redis.scard(f"{self.game_uid}_ready") == 2:
                await self.notify("start_game", "ready to play", self.game_uid)
                return True
            else:
                await self.notify("waiting", "waiting for your opponent", f"user_{user}")
                await self.notify("waiting", "your opponent is ready", f"user_{self.opponent_name}")           
            return False

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            data["user"] = self.user
        except json.JSONDecodeError:
            logger.error("❌ [PongConsumer] JSON decoding error")
            return
        
        if "command" in data:
            command = data["command"]
            if command == "start":
                if not self.game.running:
                    if await self.check_ready():
                        await self.update_game(init=True)
                        await self.start_count()

            elif command == "go":
                if not self.game.running:
                    if await redis.get(f"{self.game_uid}_paused"):
                        await redis.delete(f"{self.game_uid}_paused")
                    logger.info("🚀 [PongConsumer] Starting the game")
                    self.game.running = True
                    lock_key = f"start_game_lock_{self.game_uid}"
                    if await redis.set(lock_key, 1, nx=True, ex=60): 
                        try:
                            await asyncio.sleep(1)
                            asyncio.create_task(self.run_game_loop())               
                        finally:
                            await redis.delete(lock_key)
                else:
                    logger.warning("⚠️ [PongConsumer] The game is already running")

            elif command == "stop":
                logger.info("🛑 [PongConsumer] Stopping the game")
                await self.notify("stopped", "You have forfeited the match", self.game_uid, {"action":"forfeited"})
                self.game.running = False

            elif command == "paused":
                logger.info("🛑 [PongConsumer] Pausing the game")
                await self.notify("stopped", "your opponent paused the game", self.game_uid, {"action":"paused"})
                self.game.running = False

            elif command == "resume":
                logger.info("🛑 [PongConsumer] Resume the game")
                await self.notify("stopped", "your opponent resumed the game", self.game_uid, {"action":"resumed"})
                self.game.running = False

        if "action" in data:
            action = data["action"]
            direction = None    
            if self.user == self.game.player.user:
                direction = self.game.player.set_direction                
            elif self.user == self.game.player2.user:
                direction = self.game.player2.set_direction            
            if direction is None:
                return
            if (self.opponent == "invited"):
                direction2 = self.game.player2.set_direction
                
            if self.opponent == "invited":
                if action == "move2_up":
                    direction2(-1)
                elif action == "move2_down":
                    direction2(1)
                elif action == "stop2":
                    direction2(0)

            if action == "move_up":
                direction(-1)
            elif action == "move_down":
                direction(1)
            elif action == "stop":
                direction(0)
            await self.update_game()

    async def run_game_loop(self):
        logger.info("🔄 [PongConsumer] Starting the game loop")
        while self.game.running:
            if await redis.get(f"{self.game_uid}_paused"):
                logger.info("⏸️ [PongConsumer] Game paused, stopping loop")
                self.game.running = False
                break

            if await self.game.is_match_over():
                self.game.running = False
                break

            if not self.game.running:
                break

            await self.game.update()
            await self.update_game()
            await asyncio.sleep(seconds_to_refresh)

        if await self.game.is_match_over():
            await unlock_for_creation(self.user)            
            stats = await self.game.get_match_stats()
            await self.game.set_status("finished")
            tournament_uid = self.game.data.get("tournament_uid")            
            locked = await redis.set(f"lnotification_lock_{self.game_uid}", 1, ex=60, nx=True)
            if locked:
                if tournament_uid:
                    await self.notify("end_game", "the game is over", self.game_uid, data={"tournament_uid" : tournament_uid, "action" : "none", **stats})
                    await self.notify("end_game", "the game is over", tournament_uid, data={"tournament_uid" : tournament_uid, "action" : "tournament", **stats})
                    try :
                        await self.channel_layer.group_send(
                            tournament_uid, 
                            {"type":"launch_next", "tournament_uid" : tournament_uid, "from": self.game_uid ,"data":{"action" : "next_game", **stats}})
                    except Exception as e:
                        logger.error(f"❌ [PongConsumer] Fail sending next game request: {e}")
                else : 
                    await self.notify("end_game", "the game is over", self.game_uid, data={"tournament_uid": tournament_uid, "action" : "next_game", **stats})
            await self.save_session(stats)
            await self.cleanup()
            await self.close(code=1000)
        logger.info("⏹️  [PongConsumer] Stopping the game loop")

    
    @sync_to_async
    def save_session(self, stats):
        redis_key = f"game_result_writen:{self.game.data['game_uid']}"
        was_set = redis.set(redis_key, 1, nx=True, ex=60) #expires in 1 min
        if was_set:
            if not self.game.data['is_ai']:
                session = models.Session.objects.create(
                    player1=get_user_model().objects.get(username=self.game.data['player1']),
                    player2=get_user_model().objects.get(username=self.game.data['player2']),
                    is_multiplayer=not self.game.data['is_ai'],
                    player1_score=stats['player1']['score'],
                    player2_score=stats['player2']['score'],
                    winner_id=get_user_model().objects.get(username=stats['winner'])
                )
                if self.game.data['tournament_uid'] != False:
                    session.is_tournament = True
                    session.tournament = models.Tournament.objects.get(uuid_str=self.game.data['tournament_uid'])
                    session.save()
            else:
                if self.game.data['player1'] == 'ai':
                    session = models.Session.objects.create(
                        player2=get_user_model().objects.get(username=self.game.data['player2']),
                        is_multiplayer=not self.game.data['is_ai'],
                        player1_score=stats['player1']['score'],
                        player2_score=stats['player2']['score'],
                    )
                else:
                    session = models.Session.objects.create(
                        player1=get_user_model().objects.get(username=self.game.data['player1']),
                        is_multiplayer=not self.game.data['is_ai'],
                        player1_score=stats['player1']['score'],
                        player2_score=stats['player2']['score'],
                    )
                if stats['winner'] != 'ai':
                    session.winner_id = get_user_model().objects.get(username=stats['winner'])
                    session.save()

            logger.info(f"Game[{self.game.data['game_uid']}] is stored in the database")
        else:
            logger.info(f"Game[{self.game.data['game_uid']}] already stored")

    async def update_game(self, init=False):
        game_state = await self.game.to_dict()
        if init:
            game_state["status"] = "init"
        else:
            game_state["status"] = "running"

        if self.channel_layer:
            try:   
                await self.channel_layer.group_send(
                    self.game_uid,
                        {"type": "send_game_state", "game_state": game_state}
                    )
            except Exception as e:
                logger.error(f"❌ [PongConsumer] Error sending to Redis: {e}")
        else:
            try:
                await self.send(text_data=json.dumps(game_state))
            except Exception as e:
                logger.error(f"❌ [PongConsumer] Error sending WebSocket data: {e}")

    async def send_game_state(self, event):
        try:
            await self.send(text_data=json.dumps(event["game_state"]))
        except Exception as e:
            logger.error(f"❌ [PongConsumer] Error sending game state: {e}")

            if self.channel_layer:
                try:
                    await self.channel_layer.group_discard(self.game_uid, self.channel_name)
                    logger.info("🔗 [PongConsumer] Removed from WebSocket group")
                except Exception as e:
                    logger.error(f"❌ [PongConsumer] Error removing from WebSocket group: {e}")

            self.game.running = False

            try:
                await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                logger.warning("⚠️ [PongConsumer] Graceful game loop cancellation")
        #test

    async def acknoledge_connection(self, event):
        try:
            await self.send(text_data=json.dumps({"message":event["message"]}))
        except Exception as e:
            logger.error(f"❌ [PongConsumer] Error sending game state: {e}")

    async def start_count(self):
        for user in self.allowed_users:
            await self.tic(user)        

    async def tic (self, user):
        await self.channel_layer.group_send(f"game_user_{user}",
        {
            "type":"send_count",
            "status":"start_count"
        })

    async def send_count(self, event):
        logger.info(f"🎯 start_count called by {self.user}")
        try:
            await self.send(text_data=json.dumps({**event}))
        except Exception as e:
            logger.error(f"❌ [PongConsumer] Error sending game state: {e}")


    
class PongTournamentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.channel_layer = get_channel_layer()
        self.user = self.scope["user"].username
        self.tournament_uid = self.scope['url_route']['kwargs'].get('tournament_uid', None)
        self.CONNECTED = f"{self.tournament_uid}_connected"
        self.DISCONNECTED = f"{self.tournament_uid}_disconnected"        
        self.FIRSTCONNECT = f"{self.tournament_uid}_firstconnect"
        self.AWAITINGDISCONNECTION = f"{self.tournament_uid}_awaiting_disconnection"
        # connected = await redis.get(f"{self.tournament_uid}_connected") or 0
        if not self.channel_layer:
            logger.warning("⚠️ [TournamentConsumer] Channel Layer is None, WebSocket will function in direct mode.")
            await self.close(code=4001)
            return
        if not self.tournament_uid:
            await self.close(code=4001)
            return
        tournament_params_raw = await redis.get(self.tournament_uid)               
        if tournament_params_raw:
                tournament_params = json.loads(tournament_params_raw)
        else:
            await self.close(code=4001)
            return
        self.expected_players = int(tournament_params["expected"])# nombre de joueurs attendus
        is_ready = await is_running_tournament(self.tournament_uid)
        if (is_ready):
            self.opponent = tournament_params["game_param"]["opponent"]
            self.allowed_users = tournament_params["players"]
            if self.user in self.allowed_users:
                connected = await redis.sismember(self.CONNECTED, self.user)
                if connected:
                    #self.close(code=4001)
                    await self.close(code=4001)
                await redis.sadd(self.CONNECTED, self.user)
                await self.accept()
                logger.info("✅ [TournamentConsumer] Connection accepted")
                try:
                    await self.channel_layer.group_add(self.tournament_uid, self.channel_name)
                    await self.channel_layer.group_add(f"tournament_{self.user}", self.channel_name)
                    logger.info(f"🔗 [TournamentConsumer] {self.user} Added to WebSocket group")
                except Exception as e:
                    logger.error(f"❌ [TournamentConsumer] {self.user} Error adding to WebSocket group: {e}")
                await self.connected_message()
            else:
                await self.close(code=4001)
                logger.error(f"❌ [TournamentConsumer] user {self.user} not allowed in this tournament")
                return
        else:
            logger.error(f"❌ [TournamentConsumer] Tournament not ready")
            await self.close(code=4001)
            return
        logger.info("🖲️​ [TournamentConsumer] Initializing WebSocket...")
        notfirstconnect = await redis.sismember(self.FIRSTCONNECT, self.user)
        if notfirstconnect:
             self.tournament = active_tournaments[self.tournament_uid]  
        else:
            await redis.sadd(self.FIRSTCONNECT, self.user)
            lock_key = f"create_lock_{self.tournament_uid}"
            if await redis.set(lock_key, 1, nx=True, ex=60): 
                try:
                    if self.tournament_uid not in active_tournaments:
                        self.data = await setup_tournament_data(self.tournament_uid)
                        active_tournaments[self.tournament_uid] = Tournament(self.data)
                finally:
                    await redis.delete(lock_key)
            else:
                while self.tournament_uid not in active_tournaments:
                    await asyncio.sleep(0.05) 
            self.tournament = active_tournaments[self.tournament_uid]
            if await all_players_connected(self.allowed_users, self.CONNECTED) and len(self.allowed_users) == self.expected_players:
                await self.notify("preparing_tournament", "preparing_tournament", self.tournament_uid)
            
                if self.tournament:
                    # envoyer ici les notifications dans le chat....
                    for user in self.allowed_users:
                        date = datetime.now(timezone.utc).isoformat()
                        await self.notify("game_info", "The tournament is ready ! Please join the arena", f"room_{user}", {"date" : date})
                    was_set = await redis.set(f"init_lock_{self.tournament_uid}", value=1, nx=True, ex=60)
                    if was_set:
                        await self.tournament.init_tournament()
                        await move_game_to(self.tournament_uid, PENDING_TOURNAMENTS, RUNNING_TOURNAMENTS)
                    await self.launch_new_game()
                    await self.create_tournament_in_db()
                else:
                    await self.notify("fail", "tournament setup failed", self.tournament_uid)
                    await self.close(code=4001)

    @sync_to_async
    def create_tournament_in_db(self):
        redis_key = f"tournament_creation_writen:{self.tournament_uid}"
        was_set = redis.set(name=redis_key, value=1, nx=True, ex=60) #expires in 1 min
        if was_set:
            try:
                _, created = models.Tournament.objects.get_or_create(uuid_str=self.tournament_uid)
                if created:
                    logger.info(f"Tournament[{self.tournament_uid}] is stored in the database")
                else:
                    logger.warning(f"Tournament[{self.tournament_uid}] already existed in DB, even though Redis lock was new")
            except Exception as e:
                logger.error(f"Failed to create Tournament[{self.tournament_uid}]: {e}")
                redis.delete(redis_key)
        else:
            logger.info(f"Tournament[{self.tournament_uid}] already stored")



    async def disconnect(self, close_code):
        logger.info(f"❌ [PongTournamentConsumer] Disconnected with code {close_code}")
        connected = await redis.sismember(self.CONNECTED, self.user)
        if connected:
            await redis.srem(self.CONNECTED, self.user)
        if await redis.scard(self.CONNECTED) == 0:
            await self.cleanup()


    async def cleanup(self):
        active_tournaments.pop(self.tournament_uid, None)
        await redis.delete(self.tournament_uid)
        if await redis.sismember(RUNNING_TOURNAMENTS, self.tournament_uid):
            await redis.srem(RUNNING_TOURNAMENTS, self.tournament_uid)
        await self.channel_layer.group_discard(self.tournament_uid, self.channel_name)
        users = await redis.smembers(self.CONNECTED)
        for user in users:
            await unlock_for_creation(user)
        await redis.delete(self.CONNECTED)
        await redis.delete(self.DISCONNECTED)
        await redis.delete(self.FIRSTCONNECT)



    async def launch_new_game(self):
        current_game = None
        if not await all_games_played(self.tournament.tree):
            current_game = await get_next_game(self.tournament.tree)
        else :
            # await asyncio.sleep(0) # temporisation pour que le message de fin de tournois arrive apres celui de fin de partie du Pong Consumer
            stats = await get_tournament_stats(self.tournament.tree)
            stats["players"] = self.allowed_users
            locked = await redis.set(f"lock_{self.tournament_uid}", 1, ex=60, nx=True)   
            if locked:
                for user in self.allowed_users:
                    await self.notify("tournament_over", "the tournament is over",  f"tournament_{user}", data={
                "action":"display", "stats":stats, "tournament_uid": self.tournament_uid, "winner": stats["winner"]})
                await self.save_tournament_winner_in_db(stats["winner"])
                await redis.srem(RUNNING_TOURNAMENTS, self.tournament_uid)
            return
        if not current_game:
            logger.info("❌ [PongTournamentConsumer] : GAME NOT FOUND")
            return
        while True:
            locked = await redis.set(f"lock_{current_game.game_uid}", 1, ex=60, nx=True)
            if locked:
                users = current_game.data["allowed_users"]
                for user in users:
                    await self.notify("game_ready", "your game is ready", f"user_{user}", data={**current_game.data, "status": "game_ready"})
                active_games[current_game.game_uid] = current_game
                await asyncio.sleep(0.05)
            current_game = await get_next_game(self.tournament.tree)

            if not current_game:
                break
            else:
                logger.info(f"TRACKER in LAUNCH NEW GAME, {current_game.data}")


    @sync_to_async
    def save_tournament_winner_in_db(self, winner):
        redis_key = f"tournament_winner_writen:{self.tournament_uid}"
        was_set = redis.set(redis_key, 1, nx=True, ex=60) #expires in 1 min
        if was_set:
            tournament_model = models.Tournament.objects.get(uuid_str=self.tournament_uid)
            tournament_model.winner_id = get_user_model().objects.get(username=winner)
            tournament_model.ended_at = datetime.now(timezone.utc).isoformat()
            tournament_model.save()
            logger.info(f"Tournament[{self.tournament_uid}] winner is stored in the database")
        else:
            logger.info(f"Tournament[{self.tournament_uid}] winner already stored")


    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")
        if action:
            if action == "next_game":
                await self.launch_new_game()


    async def notify(self, status, message, recipient, data={}):
            await self.channel_layer.group_send(recipient,
            {
                "type": "notify_user",
                **data,
                "status": status,
                "message": message
            })


    async def connected_message(self):
            try:
                await self.channel_layer.group_send(
                f"user_{self.scope['user'].username}",
                    {"type": "acknoledge_connection", "message": "connected to Tournament socket"}
                )
            except Exception as e:
                logger.error(f"❌ [PongConsumer] Error sending to Redis: {e}")


    async def acknoledge_connection(self, event):
        try:
            await self.send(text_data=json.dumps({**event}))
        except Exception as e:
            logger.error(f"❌ [PongConsumer] Error sending game state: {e}")

            
    async def notify_users(self, game, status):
        key = "allowed_users"
        if not key in game:
            key = "players"
        if not key in game:
            logger.error(f"❌ [GameConsumer] Error sending game notification: bad formed request")


        for user in game[key]:
            try:
                await self.channel_layer.group_send(
                    f"user_{user}",
                    {
                        **game,
                        "type": "notify_user",
                        "status": status
                    }
                )
            except Exception as e:
                logger.error(f"❌ [GameConsumer] Error sending game notification: {e}")


    async def notify_user(self, event):
        game_uid = event.get("game_uid")
        game_param = event.get("game_param")
        if game_uid:
            event["game_uid"] = game_uid
        if game_param:
            event["game_param"] = game_param
        try:
            await self.send(text_data=json.dumps({**event}))
        except Exception as e:
            logger.error(f"❌ [PongConsumer] Error sending game announcement: {e}")

    async def launch_next(self, event):
        game_uid = event.get("from")
        if not game_uid:
            return
        locked = await redis.set(f"lock_from_{game_uid}", 1, ex=60, nx=True)
        if locked :
            await self.launch_new_game()
        else:
            return
        

    
