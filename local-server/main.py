import asyncio

from init import config
from API.websocket import LocalServer

if __name__ == "__main__":
    print("Iniciando servidor local...")

    server_url = config.WEBSOCKET_URL
    server_slug = config.SERVER_LOCAL_ID

    local_server = LocalServer(server_url, server_slug)

    asyncio.run(local_server.connect())
