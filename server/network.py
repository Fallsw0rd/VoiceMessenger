import json
import sqlite3

from config import CHUNK

clients = []


def get_db_connection():
    """Создает соединение с базой данных и выводит сообщение о статусе."""
    try:
        conn = sqlite3.connect('../data/users.db')
        conn.row_factory = sqlite3.Row
        print("Successfully connected to the database.")
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to the database: {e}")
        return None


async def handle_client(reader, writer, db_conn):
    addr = writer.get_extra_info('peername')
    clients.append(writer)
    print(f"Client connected: {addr}")

    try:
        while True:
            data = await reader.read(CHUNK)

            if not data:
                break

            try:
                # Пробуем декодировать данные как текст (JSON-команда)
                decoded_data = data.decode('utf-8').strip()
                command = json.loads(decoded_data)  # Если удается декодировать и распарсить как JSON, то это команда
                await process_request(command, writer, db_conn)
            except (UnicodeDecodeError, json.JSONDecodeError):
                # Если не удалось декодировать данные как текст, то это, вероятно, бинарные аудиоданные
                await broadcast_audio(data, writer)

    except ConnectionResetError:
        print(f"Connection reset by peer: {addr}")
    except Exception as e:
        print(f"Error with client {addr}: {e}")
    finally:
        clients.remove(writer)
        print("Closing connection.")
        writer.close()
        await writer.wait_closed()


async def process_request(command, writer, db_conn):
    """Обработка JSON-формата, таких как логин или регистрация."""
    username = command.get("username")
    password = command.get("password")

    if command.get("type") == "login":
        response = await login_user(username, password, db_conn)
        writer.write(response.encode())
        await writer.drain()

    elif command.get("type") == "register":
        response = await register_user(username, password, db_conn)
        writer.write(response.encode())
        await writer.drain()


async def broadcast_audio(data, sender_writer):
    """Пересылка аудиопотока всем клиентам, кроме отправителя."""
    for client in clients:
        if client != sender_writer:
            try:
                client.write(data)
                await client.drain()
            except Exception as e:
                print(f"Error sending audio to client: {e}")


async def register_user(username, password, db_conn):
    try:
        db_conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        db_conn.commit()
        response = {"status": "SUCCESS",
                    "message": "Успешно зарегистрировались!"}
    except sqlite3.IntegrityError:
        response = {"status": "TAKEN",
                    "message": "Такой пользователь уже существует."}
    except Exception as e:
        response = {"status": "ERROR",
                    "message": f"{e}"}

    return json.dumps(response)


async def login_user(username, password, db_conn):
    user = db_conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

    if user and user['password'] == password:
        response = {"status": "SUCCESS",
                    "message": "Успешно вошли!"}
    else:
        response = {"status": "INVALID",
                    "message": "Не удалось войти."}

    return json.dumps(response)
