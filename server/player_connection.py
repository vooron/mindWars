import json

import asyncio

import websockets

from server.player import PlayerAction


class PlayerConnection:

    action: PlayerAction
    websocket: websockets.WebSocketServerProtocol

    sync_event: asyncio.Event

    def __init__(self, websocket: websockets.WebSocketServerProtocol):
        self.websocket = websocket
        self.sync_event = asyncio.Event()

    async def send_state(self, state: dict):
        await self.websocket.send(json.dumps(state))

    async def retrieve_player_action(self, encoded_action: str):
        self.action = json.loads(encoded_action)
        self.sync_event.set()

    async def get_user_action(self):
        await self.sync_event.wait()
        self.sync_event = asyncio.Event()
        return self.action
