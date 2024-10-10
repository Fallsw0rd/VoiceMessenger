import tkinter as tk
from .gui import VoiceMessengerApp

if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceMessengerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
