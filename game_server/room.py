import json
from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import List

import asyncio

from .player import Player, PlayerAction


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
            player_action_data = await asyncio.wait_for(player.connection.get_user_action(), timeout=1)
            return PlayerAction(player, player_action_data)
        except asyncio.TimeoutError as e:
            return PlayerAction(player, None)

    async def get_players_actions(self) -> List[PlayerAction]:
        await asyncio.wait([player.connection.send_state(self.state) for player in self.players])
        return await asyncio.gather(*[self.wait_for_user_input(player) for player in self.players])

    async def start(self) -> None:

        actions_history = []
        states_history = []

        # main game cycle
        for i in range(self.MAX_ITERATIONS):
            players_actions = await self.get_players_actions()

            actions_history.append([dict(  # save copy to history
                player_login=action.player.login,
                data=dict(action.data)
            ) for action in players_actions])

            self.play(players_actions)

            states_history.append(dict(self.state))    # save copy to history

        # on finish
        for player in self.players:
            await player.connection.close(1000, "The game was finished.")

        print(f"The game was finished with status: {self.state}")

        with open(f"results/{datetime.now()}_result.json", 'w') as f:
            json.dump(dict(
                players_actions=actions_history,
                states=states_history
            ), f)
