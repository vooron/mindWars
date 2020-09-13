from typing import List

from game_server.player import PlayerAction
from game_server.room import GameRoom


class PrisonersDilemmaGameRoom(GameRoom):

    # How many players are needed to start the game.
    ROOM_SIZE: int = 2

    # How many iterations the game will take.
    MAX_ITERATIONS = 100

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

        user_actions_mapping = {
            action.player.login: action.data["decision"] if action.data is not None else True
            for action in player_actions}

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
