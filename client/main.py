import logging

import asyncio

from client.player import Player

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    player = Player(input("Enter login: "), "password")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(player.ws_handler(hostname="localhost", port=4000))
    # loop.run_forever()
