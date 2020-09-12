from server.game_server import GameServer
from server.room import PrisonsDilemmaGameRoom
import websockets
import asyncio


if __name__ == "__main__":
    server = GameServer(PrisonsDilemmaGameRoom)
    start_server = websockets.serve(server.ws_handler, 'localhost', 4000)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server)
    loop.run_forever()
