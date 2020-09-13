import logging
from abc import ABCMeta, abstractmethod
from typing import List

import asyncio

from .player import Player, PlayerAction

logging.basicConfig(level=logging.INFO)


class GameRoom(metaclass=ABCMeta):
    ROOM_SIZE: int = 2
    MAX_ITERATIONS = 100

    players: List[Player]
    is_finished: bool = False
    state: dict

    def __init__(self, players: list):
        self.players = players
        self.state = self.get_init_state()

    @abstractmethod
    def get_init_state(self) -> dict:
        """Game dependant initial state that will be sent to all gamers at the beginning
        :return: dict
        """

    @abstractmethod
    def play(self, player_actions: List[PlayerAction]):
        """Updates state according to user actions and game rules. Inplace update State.
        :param player_actions: list
        """

    async def wait_for_user_input(self, player: Player) -> PlayerAction:
        try:
            logging.info(f"wait_for_user_input before wait_for | {player.login}")
            player_action_data = await asyncio.wait_for(player.connection.get_user_action(), timeout=3)
            logging.info(f"wait_for_user_input after wait_for | {player.login}")
            return PlayerAction(player, player_action_data)
        except asyncio.TimeoutError as e:
            print("!!! TIMEOUT", e, "for", player.login)
            return PlayerAction(player, None)

    async def get_players_actions(self) -> list:
        logging.info(f"get_players_actions start")
        await asyncio.wait([player.connection.send_state(self.state) for player in self.players])
        logging.info(f"get_players_actions send state")
        return await asyncio.gather(*[self.wait_for_user_input(player) for player in self.players])

    async def start(self) -> None:
        # main game cycle
        for i in range(self.MAX_ITERATIONS):
            logging.info(f"Iteration")
            players_actions = await self.get_players_actions()
            logging.info(f"actions before play | {players_actions}")
            self.play(players_actions)
            logging.info(f"actions after play")

        # on finish
        logging.info("GAME WAS FINISHED")
        logging.info(self.state)
        for player in self.players:
            await player.connection.close(1000, "The game was finished.")
