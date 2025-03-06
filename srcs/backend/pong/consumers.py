import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from pong.game import Game
from server.logging import logger
from pong.data import DEFAULT_DATA
from channels.layers import get_channel_layer

class MyWebSocketConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info("✅ [MyWebSocketConsumer]: Connection accepted")
        await self.accept()
        await self.send(text_data=json.dumps({"message": "[MyWebSocketConsumer] connected!"}))

    async def disconnect(self, close_code):
        logger.info(f"❌ [MyWebSocketConsumer] Disconnected: {close_code}")

    async def receive(self, text_data):
        logger.info(f"📩 Message received: {text_data}")
        data = json.loads(text_data)
        message = data.get("message", "No message received")
        await self.send(text_data=json.dumps({"message": f"Echo: {message}"}))


class PongConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = "pong_game"
        self.game = Game(DEFAULT_DATA)  
        self.running = False  
        self.channel_layer = get_channel_layer()

        logger.info("🖲️​ [PongConsumer] Initializing WebSocket...")

        if not self.channel_layer:
            logger.warning("⚠️ [PongConsumer] Channel Layer is None, WebSocket will function in direct mode.")

        await self.accept()
        logger.info("✅ [PongConsumer] Connection accepted")

        if self.channel_layer:
            try:
                await self.channel_layer.group_add(self.room_name, self.channel_name)
                logger.info("🔗 [PongConsumer] Added to WebSocket group")
            except Exception as e:
                logger.error(f"❌ [PongConsumer] Error adding to WebSocket group: {e}")

        await self.update_game()

    async def receive(self, text_data):

        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            logger.error("❌ [PongConsumer] JSON decoding error")
            return

        if "command" in data:
            command = data["command"]

            if command == "start":
                if not self.running:
                    logger.info("🚀 [PongConsumer] Starting the game")
                    self.running = True
                    asyncio.create_task(self.run_game_loop())
                else:
                    logger.warning("⚠️ [PongConsumer] The game is already running")

            elif command == "stop":
                logger.info("🛑 [PongConsumer] Stopping the game")
                self.running = False
                self.game = Game(DEFAULT_DATA)
                await self.update_game()
                

        if "action" in data:
            action = data["action"]

            if action == "move_up":
                self.game.player.direction = -1
            elif action == "move_down":
                self.game.player.direction = 1
            elif action == "stop":
                self.game.player.direction = 0

        await self.update_game()

    async def run_game_loop(self):
        logger.info("🔄 [PongConsumer] Starting the game loop")

        while self.running:
            self.game.update()

            if not self.running:
                break

            await self.update_game()
            await asyncio.sleep(0.05)  

        logger.info("⏹️  [PongConsumer] Stopping the game loop")

    async def update_game(self):
        game_state = self.game.to_dict()

        if self.channel_layer:
            try:
                await self.channel_layer.group_send(
                    self.room_name,
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

    async def disconnect(self, close_code):
        logger.info(f"❌ [PongConsumer] Disconnected with code {close_code}")

        if self.channel_layer:
            try:
                await self.channel_layer.group_discard(self.room_name, self.channel_name)
                logger.info("🔗 [PongConsumer] Removed from WebSocket group")
            except Exception as e:
                logger.error(f"❌ [PongConsumer] Error removing from WebSocket group: {e}")

        self.running = False

        try:
            await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            logger.warning("⚠️ [PongConsumer] Graceful game loop cancellation")
