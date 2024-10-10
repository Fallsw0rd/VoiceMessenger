import pyaudio
import socket
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog

# Конфигурации аудио
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# Настройка PyAudio
audio = pyaudio.PyAudio()
# Создание потока для записи
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)


class VoiceMessengerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Voice Messenger")
        self.master.geometry("300x150")

        self.connect_button = tk.Button(master, text="Connect", command=self.connect_to_server)
        self.connect_button.pack(pady=20)

        self.status_label = tk.Label(master, text="Status: Disconnected")
        self.status_label.pack()

        self.sock = None

    def connect_to_server(self):
        # Запрос IP-адреса сервера
        server_ip = simpledialog.askstring("Server IP", "Enter the server IP address:")
        if not server_ip:
            return

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((server_ip, 11719))
            self.status_label.config(text="Status: Connected")
            threading.Thread(target=self.receive_audio, daemon=True).start()
            threading.Thread(target=self.send_audio, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            self.status_label.config(text="Status: Disconnected")

    def receive_audio(self):
        # Воспроизведение входящего аудио
        output_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
        while True:
            data = self.sock.recv(CHUNK)
            if not data:
                break
            output_stream.write(data)

    def send_audio(self):
        # Отправка аудио на сервер
        try:
            while True:
                data = stream.read(CHUNK)
                self.sock.sendall(data)
        except Exception as e:
            messagebox.showerror("Audio Error", str(e))

    def on_closing(self):
        if self.sock:
            self.sock.close()
        stream.stop_stream()  # Остановка потока записи
        stream.close()  # Закрытие потока
        audio.terminate()  # Освобождение ресурсов
        self.master.destroy()


# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceMessengerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
