from client.player import Player


class AnEyeForAnEyeStrategy(Player):

    def play(self, state: dict) -> dict:
        opponent_login = set(state['previous_user_actions'].keys())
        opponent_login.remove(self.login)
        opponent_login = list(opponent_login)[0]

        opponent_previous_action = state['previous_user_actions'][opponent_login]
        return dict(
            decision=opponent_previous_action
        )
