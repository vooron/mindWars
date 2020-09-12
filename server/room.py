import json
import logging
from abc import ABCMeta, abstractmethod
from typing import List

import asyncio

from .player import Player, PlayerAction

logging.basicConfig(level=logging.DEBUG)


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
            player_action_data = await asyncio.wait_for(player.connection.recv(), timeout=1)
            return PlayerAction(player, player_action_data)
        except asyncio.TimeoutError as e:
            print("TIMEOUT", e, "for", player.login)
            return PlayerAction(player, None)
        except Exception as e:
            logging.exception(f"EXCEPTION {e} for {player.login}")

    async def get_player_actions(self) -> list:
        await asyncio.wait([player.connection.send(json.dumps(self.state)) for player in self.players])
        return await asyncio.gather(*[self.wait_for_user_input(player) for player in self.players])

    async def start(self) -> None:
        logging.info("Starting game!")
        # main game cycle
        for i in range(self.MAX_ITERATIONS):
            logging.info("New iteration!")
            players_actions = await self.get_player_actions()
            logging.info(f"Player actions {players_actions}")
            self.play(players_actions)
            logging.info(f"State {self.state}")
            await asyncio.sleep(1)

        # on finish
        logging.info("GAME WAS FINISHED")
        logging.info(self.state)
        for player in self.players:
            await player.connection.close(1000, "The game was finished.")


class PrisonsDilemmaGameRoom(GameRoom):

    def get_init_state(self) -> dict:
        return dict(
            scores={player.login: 0 for player in self.players},
            previous_user_actions={  # True - cooperate
                player.login: True for player in self.players
            }
        )

    def play(self, player_actions: List[PlayerAction]) -> None:
        first_player_name: str = self.players[0].login
        second_player_name: str = self.players[1].login

        print("player_actions", player_actions)
        user_actions_mapping = {
            action.player.login: action.data["decision"] for action in player_actions if action.data is not None}

        self.state['previous_user_actions'] = user_actions_mapping

        if user_actions_mapping[first_player_name] and user_actions_mapping[second_player_name]:
            # both cooperates
            self.state['scores'][first_player_name] += 1
            self.state['scores'][second_player_name] += 1
        elif not user_actions_mapping[first_player_name] and user_actions_mapping[second_player_name]:
            self.state['scores'][first_player_name] += 2
            self.state['scores'][second_player_name] += 0
        elif user_actions_mapping[first_player_name] and not user_actions_mapping[second_player_name]:
            self.state['scores'][first_player_name] += 0
            self.state['scores'][second_player_name] += 2
        else:
            self.state['scores'][first_player_name] += 0
            self.state['scores'][second_player_name] += 0






