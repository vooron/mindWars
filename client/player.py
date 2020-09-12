import json
from abc import ABCMeta, abstractmethod

import websockets


class Player(metaclass=ABCMeta):

    login: str
    password: str

    def __init__(self, login: str, password: str):
        self.login = login
        self.password = password

    async def authenticate(self, websocket: websockets.WebSocketClientProtocol) -> None:
        await websocket.send(json.dumps(dict(
            login=self.login,
            password=self.password
        )))

    async def start(self, websocket: websockets.WebSocketClientProtocol) -> None:
        async for message in websocket:
            print("MESSAGE:", message)
            state = json.loads(message)
            print("PARSED_STATE", state)
            await websocket.send(json.dumps(dict(
                decision=True
            )))

    async def ws_handler(self, hostname: str, port: int) -> None:
        async with websockets.connect(f"ws://{hostname}:{port}") as websocket:
            await self.authenticate(websocket)
            await self.start(websocket)
            print("Finish?", websocket.closed)
