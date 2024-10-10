import asyncio

CHUNK = 1024
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 11719
clients = []


async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    clients.append(writer)
    print(f"Client connected: {addr}")
    print(clients)

    try:
        while True:
            data = await reader.read(CHUNK)
            if not data:
                print(f"Client {addr} disconnected")
                break
            # Рассылаем аудиоданные всем подключенным клиентам
            for client in clients:
                if client != writer:
                    client.write(data)
                    await client.drain()
    except:
        print(f"Connection error with client {addr}")

    clients.remove(writer)
    writer.close()
    await writer.wait_closed()


async def main():
    server = await asyncio.start_server(handle_client, SERVER_HOST, SERVER_PORT)
    async with server:
        print(f"Server started on {SERVER_HOST}:{SERVER_PORT}")
        await server.serve_forever()


asyncio.run(main())
