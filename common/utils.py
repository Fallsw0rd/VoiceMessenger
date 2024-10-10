import pyaudio


def list_audio_devices():
    p = pyaudio.PyAudio()
    device_count = p.get_device_count()
    for i in range(device_count):
        info = p.get_device_info_by_index(i)
        print(
            f"Device {i}: {info['name']}, Input Channels: {info['maxInputChannels']}, Output Channels: {info['maxOutputChannels']}")
    p.terminate()


# Вызов функции для списка устройств
if __name__ == "__main__":
    list_audio_devices()
