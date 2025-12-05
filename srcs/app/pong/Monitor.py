from .tools import RUNNING_GAMES, RUNNING_TOURNAMENTS
from server.logging import logger
import asyncio
from server.asyncredis import redis


class Monitor :

    def __init__(self, uuid, game_type):
        
        self.KEY = game_type
        self.uuid = uuid

        self.CONNECTED = f"{uuid}_connected"
        self.DISCONNECTED = f"{uuid}_disconnected"
        self.FORFEIT = f"{uuid}_forfeit"

    async def check_timeout():
        while True:
            pass