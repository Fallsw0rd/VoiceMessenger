import socket

from .config import SERVER_IP, SERVER_PORT, CHUNK


class NetworkClient:
    def __init__(self):
        self.sock = None

    def connect(self):
        """Подключение к серверу."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((SERVER_IP, SERVER_PORT))
        print(f"Connected to server at {SERVER_IP}:{SERVER_PORT}")

    def disconnect(self):
        """Отключение от сервера."""
        if self.sock:
            self.sock.close()
            self.sock = None
            print("Disconnected from server")

    def send_data(self, data):
        """Отправка данных на сервер."""
        if self.sock:
            self.sock.sendall(data)

    def receive_data(self):
        """Получение данных от сервера."""
        if self.sock:
            return self.sock.recv(CHUNK)
        return None
