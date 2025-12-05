from server.asyncredis import redis
from server.logging import logger
from django.contrib.auth import get_user_model
import json
import uuid
import secrets

# redis.set()
# redis.get()
# redis.lpush()
# redis.lrem()
# redis.llen()
# redis.sadd()
# redis.srem()

PENDING_GAMES = "pending_games"
PENDING_TOURNAMENTS = "pending_tournaments"
RUNNING_GAMES = "running_games"
RUNNING_TOURNAMENTS = "running_tournaments"
LOCKED_USERS = "locked_users"
RUNNING = "running"
PENDING = "pending"
NOSTATE = "not_found"


async def get_pseudo_or_user(username):
    if username == "pending":
        return username
    if not username or username == "":
        logger.info(f"user : {user} cant't exist")
        return None
    try : 
        user = await get_user_model().objects.aget(username=username)
        pseudo = user.tournament_pseudo
        logger.info(f"user : {user} - pseudo : {pseudo}")
        if pseudo and pseudo != "":
            return pseudo
    except get_user_model().DoesNotExist:
        logger.info(f"username : {username} not found")
        return None
    return username

async def all_players_connected(users, key):
    connected = await redis.smembers(key)
    return all(user in connected for user in users)

async def lock_for_creation(user):
    await redis.sadd(LOCKED_USERS, user)

async def unlock_for_creation(user):
    logger.info(f"                 KEY DELETE                             {user}-----------------------------")
    await redis.srem(LOCKED_USERS, user)

async def is_allowed_for_creation(user):
    is_locked = await redis.sismember(LOCKED_USERS, user)
    return not is_locked

async def get_locked_users():
    locked_users = await redis.smembers(LOCKED_USERS)
    return locked_users

async def move_game_to(game_uid, FROM , TO):
    await redis.srem(FROM, game_uid)
    await redis.sadd(TO, game_uid)

async def create_new_game(game_data, game_uid):
    await redis.set(game_uid, json.dumps(game_data))
    await redis.sadd(PENDING_GAMES, game_uid)

    
async def create_new_chat_game(game_data):
    game_uid = str(uuid.uuid4())
    await redis.set(game_uid, json.dumps(game_data), ex=180)
    await redis.sadd(PENDING_GAMES, game_uid)
    return game_uid

async def does_game_exist(game_uid):
    if not game_uid:
        return False
    exist = await redis.sismember(PENDING_GAMES, game_uid)
    if exist :
        return True
    return False


async def clean_pending_games():
    pending = await redis.smembers(PENDING_GAMES)
    for game_uid in pending:
        if not await redis.exists(game_uid):
            await redis.srem(PENDING_GAMES, game_uid)


async def is_running(game_uid, type):
    if await redis.exists(type):
        return await redis.sismember(type, game_uid)
    return False

async def is_running_tournament(game_uid):
    if await redis.exists(RUNNING_TOURNAMENTS):
        return await redis.sismember(RUNNING_TOURNAMENTS, game_uid)
    return False


async def create_new_single_game(game_data, game_uid):
        await redis.set(game_uid, json.dumps(game_data))
        await redis.sadd(RUNNING_GAMES, game_uid)
        return await lock_single_game(game_uid)

async def create_new_tournament(game_data, tournament_uid):
    await redis.set(tournament_uid, json.dumps(game_data))
    await redis.sadd(PENDING_TOURNAMENTS, tournament_uid)

async def register_tournament(user, tournament_uid):
    joined = 0
    expected = 0
    if redis.sismember(PENDING_TOURNAMENTS, tournament_uid):
        raw = await redis.get(tournament_uid)
        tournament_data = json.loads(raw)
        expected = int(tournament_data["expected"]) 
        joined = int(tournament_data["joined"])
        if joined >= expected:
            return None
        else:
            joined += 1
            lock_for_creation(user)
            tournament_data["players"].append(user)
            players = tournament_data["players"]
            logger.info(f"TRACKER REGISTER TOURNAMENT {players}")
            tournament_data["joined"] = joined
            tournament_data["status"] = "tournament_ready"
            await redis.set(tournament_uid, json.dumps(tournament_data))
            await update_game_params(tournament_uid, tournament_data)

            response = {
                    "tournament_uid": tournament_uid,
                    "status":"player_added", 
                    "created_by": tournament_data["created_by"],
                    "players": tournament_data["players"],
                    "expected":expected,
                    "joined": joined,
                    "action": "update_tournament_players",
                    f"player{joined}": joined,
                    "message" : f"{user} join the tournament"
                }
            if joined < expected:
                logger.info(f"TRACKER REGISTER TOURNAMENT {players}")
                return response 
            elif joined == expected:
                response["status"] = "tournament_full"
                response["action"] = "tournament_ready"
                logger.info(f"TRACKER REGISTER READY READY READY {players}")
                await move_game_to(tournament_uid, PENDING_TOURNAMENTS, RUNNING_TOURNAMENTS)
                return response
    return None

async def lock_tournament_game(game_uid, player1=None, player2=None):
    raw = await redis.get(game_uid)
    game = json.loads(raw)
    if player1:
        game["player1"] = player1
    if player2:
        game["player2"] = player2
    side = secrets.randbelow(2)
    if side:
        game["left"] = game["player1"]
        game["right"] = game["player2"]
        game["player1_side"] = ("left", game["player1"])
        game["player2_side"] = ("right", game["player2"])
    else:
        game["right"] = game["player1"]
        game["left"] = game["player2"]
        game["player1_side"] = ("right", game["player1"])
        game["player2_side"] = ("left", game["player2"])
    game["game_uid"] = game_uid
    game["allowed_users"] = [game["player1"], game["player2"]]
    game["status"] = "ready"
    game["from_tournament"] = True
    await update_game_params(game_uid, game)
    await move_game_to(game_uid, PENDING_GAMES, RUNNING_GAMES)
    return game


async def get_unseted_tournament_game(game_uid):
    raw = await redis.get(game_uid)
    game = json.loads(raw)
    side = secrets.randbelow(2)
    if side:
        game["left"] = game["player1"]
        game["right"] = game["player2"]
        game["player1_side"] = ("left", game["player1"])
        game["player2_side"] = ("right", game["player2"])
    else:
        game["right"] = game["player1"]
        game["left"] = game["player2"]
        game["player1_side"] = ("right", game["player1"])
        game["player2_side"] = ("left", game["player2"])
    game["allowed_users"] = [game["player1"], game["player2"]]
    game["game_uid"] = game_uid
    game["from_tournament"] = True
    game["status"] = "waiting"
    await update_game_params(game_uid, game)

    return game





async def lock_game(game_uid, user):
    raw = await redis.get(game_uid)
    game = json.loads(raw)
    if game["status"] == "ready":
        return {"game_uid": game_uid,
                "status" : "error",
            "message":"player 2 is already registered"}
    if game["created_by"] == user:
        return {"game_uid": game_uid,
                "status" : "error",
            "message":"error : same user and creator"}
    game["status"] = "ready"
    if game["players"] == 1:
        game["player2"] = user
        game["players"] = 2

        side = secrets.randbelow(2)
        logger.info(f"side : {side}")
        if side:
            game["left"] = game["player1"]
            game["right"] = user
            game["player1_side"] = ("left", game["player1"])
            game["player2_side"] = ("right", user)
        else:
            game["right"] = game["player1"]
            game["left"] = user
            game["player1_side"] = ("right", game["player1"])
            game["player2_side"] = ("left", user)
        game["allowed_users"] = [game["player1"], game["player2"]]
        game["game_uid"] = game_uid
    await redis.set(game_uid, json.dumps(game))
    await move_game_to(game_uid, PENDING_GAMES, RUNNING_GAMES)
    return game


async def lock_single_game(game_uid):
    raw = await redis.get(game_uid)
    game = json.loads(raw)
    opponent = game["game_param"]["opponent"]
    if opponent =="remote":
        return {"game_uid": game_uid,
                "status" : "error",
            "message":"bad configuration registered"}
    game["status"] = "ready"
    game["player2"] = opponent
    side = secrets.randbelow(2)
    if side:
        game["left"] = game["player1"]
        game["right"] = opponent
        game["player1_side"] = ("left", game["player1"])
        game["player2_side"] = ("right", opponent)
    else:
        game["player1_side"] = ("right", game["player1"])
        game["player2_side"] = ("left", opponent)
        game["right"] = game["player1"]
        game["left"] = opponent
    game["allowed_users"] = [game["player1"]]
    game["game_uid"] = game_uid
    await redis.set(game_uid, json.dumps(game))
    return game


async def get_game_from_status(what):
    games = []
    games_list = await redis.smembers(what)
    if games_list : 
        for game in games_list:
            if game :
                value = await redis.get(game)
                if value:
                    res = json.loads(value)
                    if res:
                        games.append(res)

    return games


async def get_game_param(game_uid):
    raw = await redis.get(game_uid)
    if raw:
        return json.loads(raw)
    else:
        logger.info(f"invalid game ! not found {game_uid}")

async def update_game_params(game_uid, dataset):
    await redis.set(game_uid, json.dumps(dataset))

async def get_game_status(game_uid):
    if await redis.sismember(RUNNING_GAMES, game_uid) or await redis.sismember(RUNNING_TOURNAMENTS, game_uid):
        return RUNNING
    elif await redis.sismember(PENDING_GAMES, game_uid) or await redis.sismember(PENDING_TOURNAMENTS, game_uid):
        return PENDING
    else:
        return NOSTATE


async def get_running_games(user):
    running = await get_game_from_status(RUNNING_GAMES)
    reco = None
    for game in running:
        if "allowed_users" in game:            
            if user in game["allowed_users"]:
                reco = game
        else:
            logger.info(f"allowed_users key not found in game : {game}")
    return reco

async def get_running_tournaments(user):
    running = await get_game_from_status(RUNNING_TOURNAMENTS)
    reco = None
    for tournament in running:
        if "players" in tournament:
            if user in tournament["players"]:
                reco = tournament
        else:
            logger.info(f"allowed_users or players key not found in tournament : {tournament}")
    return reco


def from_tournament(game):
    value = game.get("from_tournament")
    if value and value == True:
        return True
    return False


def test_key(data, key, to_test):
    if not data or not key or not to_test:
        return False
    value = data.get(key)
    if value and value == to_test:
        return True
    return False
 

async def get_all_games(user):
    tournaments = await get_game_from_status("pending_tournaments")
    games = await get_game_from_status("pending_games")
    logger.info(f"pending : {games}")
    all = { "status":"init_lobby", "tournaments" : tournaments,
           "games" : games}
    return all

