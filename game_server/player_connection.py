import json

import asyncio
import websockets


class PlayerConnection:
    _action_data: dict
    _websocket: websockets.WebSocketServerProtocol

    _sync_event: asyncio.Event

    def __init__(self, websocket: websockets.WebSocketServerProtocol):
        self._websocket = websocket
        self._sync_event = asyncio.Event()

    async def send_state(self, state: dict):
        await self._websocket.send(json.dumps(state))

    async def retrieve_player_action(self, encoded_action: str):
        self._action_data = json.loads(encoded_action)
        self._sync_event.set()

    async def get_user_action(self):
        await self._sync_event.wait()
        self._sync_event = asyncio.Event()
        return self._action_data

    async def close(self, code: int = 1000, reason: str = ""):
        await self._websocket.close(code, reason)
