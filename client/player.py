import json
from abc import ABCMeta, abstractmethod

import websockets


class Player(metaclass=ABCMeta):

    login: str
    password: str

    def __init__(self, login: str, password: str = ""):
        self.login = login
        self.password = password

    async def authenticate(self, websocket: websockets.WebSocketClientProtocol) -> None:
        # TODO: implement real auth.
        await websocket.send(json.dumps(dict(
            login=self.login,
            password=self.password
        )))

    async def start(self, websocket: websockets.WebSocketClientProtocol) -> None:
        async for message in websocket:
            state = json.loads(message)
            action_data = self.play(state)
            await websocket.send(json.dumps(action_data))

    async def ws_handler(self, hostname: str, port: int) -> None:
        async with websockets.connect(f"ws://{hostname}:{port}") as websocket:
            await self.authenticate(websocket)
            await self.start(websocket)

    @abstractmethod
    def play(self, state: dict) -> dict:
        """User implements the a Mind of the AI, that will react on the current state,
        create an action that will change the state on a server.
        :param state: dict - current state that was sent from the server
        :return: action data - will be transferred to server to update the state
        """
