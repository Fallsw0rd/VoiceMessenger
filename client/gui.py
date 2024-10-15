import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from audio import AudioHandler
from network import NetworkClient


def center_window(width, height, window):
    """Центрирует окно на экране с заданной шириной и высотой."""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)

    window.geometry(f"{width}x{height}+{x}+{y}")


class VoiceMessengerApp:
    def __init__(self, master):
        self.master = master
        self.network_client = NetworkClient()
        self.audio_handler = AudioHandler()

        # Центрирование окна и убираем стандартную рамку
        center_window(400, 300, master)

        # Настройка основного окна
        self.master.geometry("400x300")
        self.master.configure(bg="#36393F")  # Темный фон
        self.master.title("Voice Messenger")

        # Создание стиля для кнопок и меток
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 12), padding=10, background="#5865F2", foreground="white",
                        relief="flat")
        style.map("TButton", background=[("active", "#404EED")], foreground=[("active", "white")])

        # Задание стиля для меток
        style.configure("TLabel", background="#36393F", foreground="white", font=("Segoe UI", 12))

        self.is_connected = False

        self.setup_interface()

    def open_messenger(self, username):
        """Открывает основное окно мессенджера после успешной авторизации."""
        messenger_window = tk.Toplevel(self.master)
        messenger_window.title(f"Voice Messenger - {username}")
        messenger_window.geometry("1200x600")
        messenger_window.configure(bg="#36393F")
        center_window(1200, 600, messenger_window)

        # Статус соединения
        self.status_label = ttk.Label(messenger_window, text="Status: Disconnected", style="TLabel")
        self.status_label.pack(pady=10)

        # Кнопка соединения
        self.connect_button = ttk.Button(messenger_window, text="Connect", command=self.toggle_connection,
                                         style="TButton")
        self.connect_button.pack(pady=20)

        self.is_connected = False

    def setup_interface(self):
        # Ввод имени пользователя
        self.label_username = ttk.Label(self.master, text="Username:")
        self.label_username.pack(pady=5)
        self.entry_username = ttk.Entry(self.master)
        self.entry_username.pack(pady=5)

        # Ввод пароля
        self.label_password = ttk.Label(self.master, text="Password:")
        self.label_password.pack(pady=5)
        self.entry_password = ttk.Entry(self.master, show="*")
        self.entry_password.pack(pady=5)

        # Кнопка входа
        self.login_button = ttk.Button(self.master, text="Login", command=self.login)
        self.login_button.pack(pady=5)

        # Кнопка регистрации
        self.register_button = ttk.Button(self.master, text="Register", command=self.register)
        self.register_button.pack(pady=5)

    def login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        # Отправка запроса на сервер
        response = self.network_client.send_request("login", username, password)
        if response and response["status"] == "SUCCESS":
            messagebox.showinfo("Login Successful", response['message'])
            self.master.withdraw()
            self.open_messenger(username)
        else:
            messagebox.showerror("Error", response['message'] if response else "No response from server")

    def register(self):
        username = self.entry_username.get()
        password = self.entry_password.get()

        # Отправка запроса на сервер
        response = self.network_client.send_request("register", username, password)
        if response and response["status"] == "SUCCESS":
            messagebox.showinfo("Success", response['message'])
        elif response and response["status"] == "TAKEN":
            messagebox.showerror("Taken", response['message'])
        elif response and response["status"] == "ERROR":
            messagebox.showerror("Error", response['message'] if response else "No response from server")

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
        # Отключение от сервера
        self.network_client.disconnect()

        # Остановим аудиопотоки перед отключением
        self.audio_handler.stop_stream()

        self.status_label.config(text="Status: Disconnected")
        self.connect_button.config(text="Connect")
        self.is_connected = False

    def on_closing(self):
        if self.is_connected:
            self.disconnect_from_server()
        self.master.destroy()
