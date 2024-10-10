import tkinter as tk
from tkinter import messagebox

from .audio import AudioHandler
from .network import NetworkClient


class VoiceMessengerApp:
    def __init__(self, master):
        self.master = master
        self.network_client = NetworkClient()
        self.audio_handler = AudioHandler()

        # Создание интерфейса
        self.connect_button = tk.Button(master, text="Connect", command=self.toggle_connection)
        self.connect_button.pack(pady=10)

        self.status_label = tk.Label(master, text="Status: Disconnected")
        self.status_label.pack(pady=5)

        self.is_connected = False  # Флаг состояния соединения

    def toggle_connection(self):
        if self.is_connected:
            self.disconnect_from_server()
        else:
            self.connect_to_server()

    def connect_to_server(self):
        try:
            self.network_client.connect()
            self.status_label.config(text="Status: Connected")
            self.is_connected = True
            self.connect_button.config(text="Disconnect")

            # Запуск потоков отправки и получения аудио
            self.audio_handler.start_stream(self.network_client.sock)

        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            self.status_label.config(text="Status: Disconnected")
            self.is_connected = False

    def disconnect_from_server(self):
        self.network_client.disconnect()
        self.audio_handler.stop_stream()
        self.status_label.config(text="Status: Disconnected")
        self.connect_button.config(text="Connect")
        self.is_connected = False

    def on_closing(self):
        if self.is_connected:
            self.disconnect_from_server()
        self.master.destroy()
