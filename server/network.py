from .config import CHUNK
clients = []


async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    clients.append(writer)
    print(f"Client connected: {addr}")

    try:
        while True:
            data = await reader.read(CHUNK)
            if not data:
                break  # Если данных нет, клиент отключился
            await process_request(data, writer)

    except ConnectionResetError:
        print(f"Connection reset by peer: {addr}")
    except Exception as e:
        print(f"Error with client {addr}: {e}")
    finally:
        clients.remove(writer)
        print("Closing connection.")
        writer.close()
        await writer.wait_closed()


async def process_request(data, writer):
    for client in clients:
        if client != writer:
            client.write(data)
            await client.drain()
