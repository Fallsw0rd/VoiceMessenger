import asyncio

from config import SERVER_HOST, SERVER_PORT
from network import handle_client, get_db_connection


async def main():
    db_conn = get_db_connection()
    if db_conn is None:
        print("Failed to connect to the database. Exiting.")
        return

    server = await asyncio.start_server(lambda r, w: handle_client(r, w, db_conn), SERVER_HOST, SERVER_PORT)
    async with server:
        print(f"Server started on {SERVER_HOST}:{SERVER_PORT}")
        await server.serve_forever()

    db_conn.close()

if __name__ == "__main__":
    asyncio.run(main())
