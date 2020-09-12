from dataclasses import dataclass
from typing import Optional

from server.player_connection import PlayerConnection


@dataclass
class Player:
    connection: PlayerConnection
    login: str


@dataclass
class PlayerAction:
    player: Player
    data: Optional[dict]
