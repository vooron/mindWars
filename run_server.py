import asyncio
import websockets

from custom_game_rooms.prisons_dilemma_room import PrisonersDilemmaGameRoom
from custom_game_rooms.worm_game_room import WormGameRoom
from game_server.game_server import GameServer


if __name__ == "__main__":
    server = GameServer(WormGameRoom)
    start_server = websockets.serve(server.ws_handler, 'localhost', 4000)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server)
    loop.run_forever()
