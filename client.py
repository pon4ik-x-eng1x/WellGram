import tkinter as tk
from tkinter import simpledialog, messagebox
import websocket
import json
import threading
import time

class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Client")

        self.username = None
        self.room = None

        self.ws = websocket.WebSocketApp("ws://localhost:5000/socket.io/?EIO=4&transport=websocket",
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws_thread = threading.Thread(target=self.run_ws)
        self.ws_thread.start()

        self.create_ui()

    def run_ws(self):
        while True:
            try:
                self.ws.run_forever()
            except Exception as e:
                print(f"WebSocket error: {e}")
                time.sleep(5)  # Подождите 5 секунд перед повторной попыткой

    def create_ui(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.username_label = tk.Label(self.main_frame, text="Username:")
        self.username_label.pack(pady=5)

        self.username_entry = tk.Entry(self.main_frame)
        self.username_entry.pack(pady=5)

        self.register_button = tk.Button(self.main_frame, text="Register", command=self.register)
        self.register_button.pack(pady=5)

        self.chat_frame = tk.Frame(self.main_frame)
        self.chat_frame.pack(fill=tk.BOTH, expand=True)

        self.messages_text = tk.Text(self.chat_frame, state='disabled')
        self.messages_text.pack(fill=tk.BOTH, expand=True)

        self.message_entry = tk.Entry(self.main_frame)
        self.message_entry.pack(pady=5, fill=tk.X, padx=10)

        self.send_button = tk.Button(self.main_frame, text="Send", command=self.send_message)
        self.send_button.pack(pady=5)

        self.room_var = tk.StringVar(value="Select Chat Room")
        self.room_menu = tk.OptionMenu(self.main_frame, self.room_var, "Room 1", "Room 2")
        self.room_menu.pack(pady=5)

        self.room_var.trace("w", self.change_room)

    def register(self):
        self.username = self.username_entry.get()
        if not self.username:
            messagebox.showerror("Error", "Username cannot be empty")
            return

        try:
            self.ws.send(json.dumps({"username": self.username}))
        except Exception as e:
            print(f"Error sending message: {e}")
            messagebox.showerror("Error", "Failed to send registration request")
        self.main_frame.pack_forget()
        self.chat_frame.pack(fill=tk.BOTH, expand=True)

    def send_message(self):
        if not self.ws.sock or not self.ws.sock.connected:
            print("WebSocket connection is not open.")
            return
        message = self.message_entry.get()
        if message:
            try:
                self.ws.send(json.dumps({"room": self.room, "message": message, "username": self.username}))
                self.message_entry.delete(0, tk.END)
            except Exception as e:
                print(f"Error sending message: {e}")

    def change_room(self, *args):
        new_room = self.room_var.get()
        if self.room and self.username:
            try:
                self.ws.send(json.dumps({"room": self.room, "username": self.username, "action": "leave"}))
            except Exception as e:
                print(f"Error sending leave room message: {e}")
        if new_room != "Select Chat Room":
            self.room = new_room
            try:
                self.ws.send(json.dumps({"room": self.room, "username": self.username, "action": "join"}))
            except Exception as e:
                print(f"Error sending join room message: {e}")

    def on_message(self, ws, message):
        data = json.loads(message)
        if 'username' in data and 'message' in data:
            self.messages_text.config(state='normal')
            self.messages_text.insert(tk.END, f"{data['username']}: {data['message']}\n")
            self.messages_text.config(state='disabled')

    def on_error(self, ws, error):
        print(f"Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("### closed ###")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClient(root)
    root.mainloop()
