from typing import List

from game_server.player import PlayerAction
from game_server.room import GameRoom

import random


class WormGameRoom(GameRoom):

    # How many players are needed to start the game.
    ROOM_SIZE: int = 3

    # How many iterations the game will take.
    MAX_ITERATIONS = 100

    BOARD_SIZE = (25, 25)
    WORM_LENGTH = 5

    def generate_initial_worms_positions(self):
        # true if object in this cell
        board_mask = [[False for j in range(self.BOARD_SIZE[1])] for i in range(self.BOARD_SIZE[0])]

        worms_positions = {}
        for player in self.players:
            worms_positions[player.login] = []

            is_free = False
            # get tail position
            i, j = None, None
            while not is_free:
                i, j = random.randint(0, self.BOARD_SIZE[0] - 1), random.randint(0, self.BOARD_SIZE[1] - 1)
                is_free = not board_mask[i][j]

            worms_positions[player.login].append((i, j))
            board_mask[i][j] = True

            for _ in range(self.WORM_LENGTH):
                if not board_mask[i - 1][j] or i - 1 < 0:
                    worms_positions[player.login].append((i - 1, j))
                    i -= 1
                    board_mask[i][j] = True
                    continue
                elif not board_mask[i + 1][j] or i + 1 >= self.BOARD_SIZE[0]:
                    worms_positions[player.login].append((i + 1, j))
                    i += 1
                    board_mask[i][j] = True
                    continue
                elif not board_mask[i][j - 1] or j - 1 < 0:
                    worms_positions[player.login].append((i, j - 1))
                    j -= 1
                    board_mask[i][j] = True
                    continue
                elif not board_mask[i][j + 1] or j + 1 >= self.BOARD_SIZE[1]:
                    worms_positions[player.login].append((i, j + 1))
                    j += 1
                    board_mask[i][j] = True
                    continue
                else:
                    return self.generate_initial_worms_positions()  # get a collision. Try again

        return worms_positions

    def get_init_state(self) -> dict:
        return dict(
            board_size=self.BOARD_SIZE,
            players_scores={player.login: 0 for player in self.players},
            players_statuses={player.login: True for player in self.players},
            players_positions=self.generate_initial_worms_positions(),
            previous_player_actions={player.login: "UP" for player in self.players}
        )

    def play(self, player_actions: List[PlayerAction]) -> None:
        """Player action data: {direction: (LEFT, RIGHT, UP, DOWN)}"""
        player_actions_mapping = {
            action.player.login:
                (action.data['direction'] if action.data is not None
                 else self.state['previous_player_actions'][action.player.login])
            for action in player_actions}

        if not any(self.state['players_statuses'].values()):
            self.end_game("All players dead")

        for player in self.players:

            if not self.state['players_statuses'][player.login]:
                continue

            prev_position = self.state['players_positions'][player.login][-1]
            if player_actions_mapping[player.login] == "UP":
                position = (prev_position[0] + 1, prev_position[1])
            elif player_actions_mapping[player.login] == "DOWN":
                position = (prev_position[0] - 1, prev_position[1])
            elif player_actions_mapping[player.login] == "LEFT":
                position = (prev_position[0], prev_position[1] - 1)
            else:
                position = (prev_position[0], prev_position[1] + 1)

            self.state['previous_player_actions'][player.login] = player_actions_mapping[player.login]

            for opponent_player in self.players:  # if collate with body of opponent or itself - die.
                if self.state['players_statuses'][opponent_player.login] and \
                        position in self.state['players_positions'][opponent_player.login][1:]:
                    self.state['players_statuses'][player.login] = False
                    print(f"Player {player.login} are dead. Collate with someone body.")

            self.state['players_positions'][player.login] = self.state['players_positions'][player.login][1:]
            self.state['players_positions'][player.login].append(position)

            if (position[0] < 0 or position[0] >= self.BOARD_SIZE[0] or  # if out of the board - die
                    position[1] < 0 or position[1] >= self.BOARD_SIZE[1]):
                self.state['players_statuses'][player.login] = False
                print(f"Player {player.login} are dead. Out of board.")

        for player in self.players:
            for opponent_player in self.players:  # if heads collate - die both
                if player.login == opponent_player.login:
                    continue
                if self.state['players_statuses'][player.login] and self.state['players_statuses'][opponent_player.login]:
                    if self.state['players_positions'][player.login][-1] == self.state['players_positions'][opponent_player.login][-1]:
                        self.state['players_statuses'][player.login] = False
                        self.state['players_statuses'][opponent_player.login] = False
                        print(f"Players {player.login} and {opponent_player.login} are dead.")

        for player in self.players:
            if self.state['players_statuses'][player.login]:
                self.state['players_scores'][player.login] += 1
