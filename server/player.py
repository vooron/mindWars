from dataclasses import dataclass
from typing import Optional

import websockets


class Player:
    connection: websockets.WebSocketServerProtocol
    login: str

    def __init__(self, websocket: websockets.WebSocketServerProtocol, login: str):
        self.connection = websocket
        self.login = login


@dataclass
class PlayerAction:
    player: Player
    data: Optional[dict]
