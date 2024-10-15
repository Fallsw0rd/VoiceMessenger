import threading

import pyaudio

from config import CHUNK, FORMAT, CHANNELS, RATE


class AudioHandler:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.input_stream = None
        self.output_stream = None
        self.send_audio_thread = None
        self.receive_audio_thread = None
        self.is_streaming = False

    def start_stream(self, sock):
        """Запуск потоков для отправки и получения аудио данных."""
        if self.is_streaming:
            print("Audio stream is already running.")
            return

        try:
            # Получаем устройства по умолчанию для ввода и вывода
            input_device_index = int(self.audio.get_default_input_device_info()['index'])
            output_device_index = int(self.audio.get_default_output_device_info()['index'])

            # Выводим информацию о выбранных устройствах
            # input_device_info = self.audio.get_device_info_by_index(input_device_index)
            # output_device_info = self.audio.get_device_info_by_index(output_device_index)
            # print(f"Selected Input Device: {input_device_info['name']}")
            # print(f"Selected Output Device: {output_device_info['name']}")

            # Инициализация потоков с использованием устройств по умолчанию
            self.input_stream = self.audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True,
                                                frames_per_buffer=CHUNK, input_device_index=input_device_index)
            self.output_stream = self.audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True,
                                                 frames_per_buffer=CHUNK, output_device_index=output_device_index)

            self.is_streaming = True

            # Запуск потока для отправки аудио данных на сервер
            self.send_audio_thread = threading.Thread(target=self.send_audio, args=(sock,))
            self.send_audio_thread.start()

            # Запуск потока для получения аудио данных с сервера и их воспроизведения
            self.receive_audio_thread = threading.Thread(target=self.receive_audio, args=(sock,))
            self.receive_audio_thread.start()

        except Exception as e:
            print(f"Error starting audio stream: {e}")
            self.stop_stream()  # Остановить поток в случае ошибки

    def send_audio(self, sock):
        """Чтение аудиоданных с микрофона и отправка их на сервер."""
        try:
            while self.is_streaming:
                data = self.input_stream.read(CHUNK, exception_on_overflow=False)
                sock.sendall(data)
        except Exception as e:
            print(f"Error sending audio: {e}")

    def receive_audio(self, sock):
        """Получение аудиоданных с сервера и их воспроизведение."""
        try:
            while self.is_streaming:
                data = sock.recv(CHUNK)
                if not data:
                    print("No data received, closing the stream.")
                    break
                self.output_stream.write(data)
        except ConnectionResetError:
            print("Connection was reset by the server.")
        except Exception as e:
            print(f"Error receiving audio: {e}")

    def stop_stream(self):
        """Остановка аудио потоков и завершение работы."""
        if not self.is_streaming:
            print("Audio stream is not running.")
            return

        self.is_streaming = False

        # Ожидание завершения потоков
        if self.send_audio_thread:
            self.send_audio_thread.join()
            self.send_audio_thread = None

        if self.receive_audio_thread:
            self.receive_audio_thread.join()
            self.receive_audio_thread = None

        # Закрытие потоков
        if self.input_stream:
            self.input_stream.stop_stream()
            self.input_stream.close()
            self.input_stream = None

        if self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()
            self.output_stream = None

        self.audio.terminate()
        print("Audio stream stopped successfully.")
