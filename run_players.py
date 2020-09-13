from multiprocessing import Pool

import asyncio

from custom_players.an_eye_for_an_eye_strategy import AnEyeForAnEyeStrategy
from custom_players.random_player import RandomStrategy

CONFIG = [
    dict(
        client_class=AnEyeForAnEyeStrategy,
        name="First User (An eye for an eye)"
    ),
    dict(
        client_class=RandomStrategy,
        name="Second User (Random(30% True)"
    )
]


def run_single_client(data):
    client_class = data['client_class']
    name = data['name']
    player = client_class(name)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(player.ws_handler(hostname="localhost", port=4000))


if __name__ == "__main__":
    pool = Pool(processes=len(CONFIG))
    pool.map(run_single_client, CONFIG)
    pool.close()
