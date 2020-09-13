import random

from client.player import Player


class RandomDirectionStrategy(Player):
    N_TRIES = 10

    def build_board(self, players_positions: dict, board_size: list) -> list:
        board_mask = [[False for j in range(board_size[1])] for i in range(board_size[0])]

        for player, positions in players_positions.items():
            for p in positions[1:]:
                board_mask[p[0]][p[1]] = True

        return board_mask

    def play(self, state: dict) -> dict:

        if not state['players_statuses'][self.login]:
            return dict(direction="UP")  # the worm is dead. The direction doesn't matter

        worm_head = state['players_positions'][self.login][-1]
        board = self.build_board(state['players_positions'], state['board_size'])

        direction = "UP"

        for _ in range(self.N_TRIES):

            worm_head_current = list(worm_head)

            decision = random.randint(0, 3)
            if decision == 0:
                direction = "UP"
                worm_head_current[0] += 1
            elif decision == 1:
                direction = "DOWN"
                worm_head_current[0] -= 1
            elif decision == 2:
                direction = "LEFT"
                worm_head_current[1] -= 1
            elif decision == 3:
                direction = "RIGHT"
                worm_head_current[1] += 1

            if worm_head_current[0] >= state['board_size'][0] or worm_head_current[0] < 0 \
                    or worm_head_current[1] < 0 or worm_head_current[1] >= state['board_size'][1]:
                continue

            if board[worm_head_current[0]][worm_head_current[1]]:
                continue

            return dict(direction=direction)
