import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from .audio import AudioHandler
from .network import NetworkClient


class VoiceMessengerApp:
    def __init__(self, master):
        self.master = master
        self.network_client = NetworkClient()
        self.audio_handler = AudioHandler()

        # Передаем ширину и высоту окна
        self.center_window(400, 300)

        # Убираем стандартную рамку окна
        self.master.overrideredirect(True)

        # Настройка основного окна
        self.master.geometry("400x300")
        self.master.configure(bg="#36393F")  # Темный фон в стиле Discord

        # Создание кастомной панели заголовка
        self.title_bar = tk.Frame(self.master, bg="#2F3136", relief="raised", bd=0, height=30)
        self.title_bar.pack(fill=tk.X)

        # Создание кнопки закрытия окна
        self.close_button = tk.Button(self.title_bar, text="✖", command=self.on_closing, bg="#2F3136",
                                      fg="white", bd=0, font=("Arial", 12), padx=5, pady=2)
        self.close_button.pack(side=tk.RIGHT, padx=5)

        # Создание названия окна
        self.title_label = tk.Label(self.title_bar, text="Voice Messenger", bg="#2F3136", fg="white",
                                    font=("Arial", 12))
        self.title_label.pack(side=tk.LEFT, padx=10)

        # Создание стиля для кнопок и меток
        style = ttk.Style()

        # Задание стиля для кнопок
        style.theme_use("clam")  # Используем тему, которая лучше поддерживает настройки цвета
        style.configure("TButton", font=("Segoe UI", 12), padding=10, background="#5865F2", foreground="white",
                        relief="flat")
        style.map("TButton", background=[("active", "#404EED")], foreground=[("active", "white")])

        # Задание стиля для меток
        style.configure("TLabel", background="#36393F", foreground="white", font=("Segoe UI", 12))

        # Создание интерфейса
        self.connect_button = ttk.Button(master, text="Connect", command=self.toggle_connection, style="TButton")
        self.connect_button.pack(pady=20)

        self.status_label = ttk.Label(master, text="Status: Disconnected", style="TLabel")
        self.status_label.pack(pady=10)

        self.is_connected = False

        # Добавляем возможность перемещать окно за кастомную панель заголовка
        self.title_bar.bind("<ButtonPress-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.on_motion)

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

# Интерфейс
    def on_closing(self):
        if self.is_connected:
            self.disconnect_from_server()
        self.master.destroy()

    def center_window(self, width, height):
        """Центрирует окно на экране с заданной шириной и высотой."""
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()

        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        self.master.geometry(f"{width}x{height}+{x}+{y}")

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def on_motion(self, event):
        x = (event.x_root - self.x)
        y = (event.y_root - self.y)
        self.master.geometry(f"+{x}+{y}")
