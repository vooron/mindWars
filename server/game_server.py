import json
import logging
from typing import Type

import websockets

from .player_connection import PlayerConnection

logging.basicConfig(level=logging.DEBUG)

from .player import Player
from .room import GameRoom


class GameServer:
    _room_type: Type[GameRoom]

    _rooms: list
    _queue: list

    def __init__(self, room_type: Type[GameRoom]):
        self._room_type = room_type
        self._queue = list()
        self._rooms = list()

    def _is_auth_data_valid(self, auth_data: dict) -> bool:
        if not auth_data.get("login") or not auth_data.get("password"):
            return False
        return True

    async def _validate_user_can_connect(self, login: str) -> bool:
        return True

    async def register(self, websocket: websockets.WebSocketServerProtocol, connection: PlayerConnection) -> None:
        auth_raw = await websocket.recv()
        try:
            auth = json.loads(auth_raw)
            if not self._is_auth_data_valid(auth):
                await websocket.close(1007, "Auth payload invalid.")
                return

            if not await self._validate_user_can_connect(auth['login']):
                await websocket.close(1007, "User are not permitted to connect")

            self._queue.append(Player(connection, auth['login']))

            logging.info(f"{websocket.remote_address} with name {auth['login']} connects.")
            await websocket.send("{}")
        except Exception as e:
            logging.exception("=======EEEEEXCEPTION", e)
            await websocket.close(1007, "Error while trying to authenticate.")

    async def try_create_new_room(self) -> None:
        if len(self._queue) >= self._room_type.ROOM_SIZE:
            room = self._room_type(self._queue[:self._room_type.ROOM_SIZE])
            self._rooms.append(room)
            self._queue = self._queue[self._room_type.ROOM_SIZE:]
            logging.info("Room was created!")
            await room.start()
            logging.info("Game was started!")

    async def ws_handler(self, websocket: websockets.WebSocketServerProtocol, _: str) -> None:
        connection = PlayerConnection(websocket)
        await self.register(websocket, connection)
        await self.try_create_new_room()

        async for message in websocket:
            await connection.retrieve_player_action(message)

        print("END ws handler", self._queue)
