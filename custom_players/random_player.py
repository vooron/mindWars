import random

from client.player import Player


class RandomStrategy(Player):

    def play(self, state: dict) -> dict:
        return dict(
            decision=random.uniform(0, 1) > 0.7  # will not cooperate in 70%
        )
