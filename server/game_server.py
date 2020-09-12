import json
import logging
from typing import Type

import websockets

logging.basicConfig(level=logging.DEBUG)

from .player import Player
from .room import GameRoom


class GameServer:
    room_type: Type[GameRoom]

    rooms: list
    queue: list

    def __init__(self, room_type: Type[GameRoom]):
        self.room_type = room_type
        self.queue = list()
        self.rooms = list()

    def _is_auth_data_valid(self, auth_data: dict) -> bool:
        if not auth_data.get("login") or not auth_data.get("password"):
            return False
        return True

    async def _validate_user_can_connect(self, login: str) -> bool:
        return True

    async def register(self, websocket: websockets.WebSocketServerProtocol) -> None:
        auth_raw = await websocket.recv()
        print("AUTH_RAW", auth_raw)
        try:
            auth = json.loads(auth_raw)
            if not self._is_auth_data_valid(auth):
                print("CLOSING!")
                await websocket.close(1007, "Auth payload invalid.")
                return

            if not await self._validate_user_can_connect(auth['login']):
                print("CLOSING!")
                await websocket.close(1007, "User are not permitted to connect")

            self.queue.append(Player(websocket, auth['login']))
            logging.info(f"{websocket.remote_address} with name {auth['login']} connects.")
            await websocket.send("{}")
        except Exception as e:
            logging.exception("=======EEEEEXCEPTION", e)
            await websocket.close(1007, "Error while trying to authenticate.")

    async def try_create_new_room(self) -> None:
        if len(self.queue) >= self.room_type.ROOM_SIZE:
            room = self.room_type(self.queue[:self.room_type.ROOM_SIZE])
            self.rooms.append(room)
            self.queue = self.queue[self.room_type.ROOM_SIZE:]
            logging.info("Room was created!")
            await room.start()
            logging.info("Game was started!")

    async def ws_handler(self, websocket: websockets.WebSocketServerProtocol, _: str) -> None:
        await self.register(websocket)
        await self.try_create_new_room()
        print("END ws handler", self.queue)
