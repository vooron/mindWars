import asyncio
import json
import logging
from typing import Type

import websockets

from .player_connection import PlayerConnection

logging.basicConfig(level=logging.INFO)

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
        if not auth_data.get("login"):  # or not auth_data.get("password"):
            return False
        return True

    async def _validate_user_can_connect(self, login: str) -> bool:
        return True

    async def register(self, websocket: websockets.WebSocketServerProtocol, connection: PlayerConnection) -> None:
        logging.info("Register start")
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
        except Exception as e:
            logging.exception("=======EEEEEXCEPTION", e)
            await websocket.close(1007, "Error while trying to authenticate.")

    async def try_create_new_room(self) -> None:
        logging.info("try_create_new_room")
        if len(self._queue) >= self._room_type.ROOM_SIZE:
            logging.info("try_create_new_room TRUE")
            room = self._room_type(self._queue[:self._room_type.ROOM_SIZE])
            self._rooms.append(room)
            self._queue = self._queue[self._room_type.ROOM_SIZE:]
            logging.info("Room was created!")
            await room.start()
            logging.info("try_create_new_room END")

    async def subscribe_to_messages(self, websocket: websockets.WebSocketServerProtocol, connection: PlayerConnection):
        logging.info(f"Before subscribe {websocket}")
        async for message in websocket:
            logging.info(f"message from {websocket}")
            await connection.retrieve_player_action(message)

    async def ws_handler(self, websocket: websockets.WebSocketServerProtocol, _: str) -> None:
        connection = PlayerConnection(websocket)
        await self.register(websocket, connection)

        await asyncio.wait((
            self.try_create_new_room(),
            self.subscribe_to_messages(websocket, connection)
        ))
