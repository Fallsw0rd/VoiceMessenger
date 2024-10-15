import json
import socket

from config import SERVER_IP, SERVER_PORT, CHUNK


class NetworkClient:
    def __init__(self):
        self.sock = None
        self.is_connected = False

    def connect(self):
        """Подключение к серверу."""
        if not self.is_connected:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((SERVER_IP, SERVER_PORT))
                self.is_connected = True
            except socket.error as e:
                self.is_connected = False

    def disconnect(self):
        """Отключение от сервера."""
        if self.sock:
            self.sock.close()
            self.sock = None
            self.is_connected = False
            print("Disconnected from server")

    def send_data(self, data):
        """Отправка данных на сервер."""
        if self.is_connected:
            try:
                self.sock.sendall(data)
            except socket.error as e:
                print(f"Failed to send data: {e}")
                self.disconnect()

    def receive_data(self):
        """Получение данных от сервера."""
        if self.is_connected:
            try:
                return self.sock.recv(CHUNK)
            except socket.error as e:
                print(f"Failed to receive data: {e}")
                self.disconnect()
        return None

    def send_request(self, request_type, username, password):
        """Отправляет запрос на сервер и получает ответ."""
        if not self.is_connected:
            self.connect()

        if self.is_connected:
            message = {
                "type": request_type,
                "username": username,
                "password": password
            }
            request_json = json.dumps(message).encode('utf-8')

            # Отправка данных на сервер
            self.send_data(request_json)

            # Получаем ответ от сервера
            response = self.receive_data()
            return json.loads(response.decode('utf-8')) if response else None
        else:
            print("Unable to send request, no connection to server.")
            return None
