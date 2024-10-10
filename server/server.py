import asyncio

from .config import SERVER_HOST, SERVER_PORT
from .network import handle_client


async def main():
    server = await asyncio.start_server(handle_client, SERVER_HOST, SERVER_PORT)
    async with server:
        print(f"Server started on {SERVER_HOST}:{SERVER_PORT}")
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
