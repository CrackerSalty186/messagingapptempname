import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog, filedialog
from tkinter import ttk
from PIL import Image, ImageTk
import io

HOST = '127.0.0.1'
PORT = 12345        

class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Client")
        self.username = simpledialog.askstring("Username", "Enter your username", parent=self.root)
        if not self.username:
            self.username = "Guest"

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((HOST, PORT))
        self.client_socket.send(self.username.encode('utf-8'))
        threading.Thread(target=self.receive_messages, daemon=True).start()

        self.chat_area = scrolledtext.ScrolledText(self.root, state='disabled', wrap=tk.WORD)
        self.chat_area.pack(padx=10, pady=10, side=tk.LEFT)

        self.message_input = tk.Entry(self.root, width=50)
        self.message_input.pack(padx=10, pady=(0, 10))
        self.message_input.bind("<Return>", self.send_message)

        send_button = tk.Button(self.root, text="Send", command=self.send_message)
        send_button.pack(pady=(0, 10))

        emoji_label = tk.Label(self.root, text="Select Emoji:")
        emoji_label.pack(padx=10, pady=(0, 5))
        
        emoji_options = ["😀", "😂", "😍", "😎", "😭", "😡", "👍", "🙌", "🔥", "✨", "🎉"]
        self.emoji_picker = ttk.Combobox(self.root, values=emoji_options, state='readonly')
        self.emoji_picker.pack(padx=10, pady=(0, 5))
        self.emoji_picker.bind("<<ComboboxSelected>>", self.add_emoji)

        attach_button = tk.Button(self.root, text="Attach Image", command=self.attach_image)
        attach_button.pack(pady=(0, 10))

        self.user_listbox = tk.Listbox(self.root, height=10)
        self.user_listbox.pack(padx=10, pady=10, side=tk.RIGHT)

    def add_emoji(self, event=None):
        emoji = self.emoji_picker.get()
        self.message_input.insert(tk.END, emoji)

    def send_message(self, event=None):
        message = self.message_input.get()
        if message:
            if message.startswith("/dm"):
                self.client_socket.send(message.encode('utf-8'))
            else:
                self.client_socket.send(message.encode('utf-8'))
                self.chat_area.config(state='normal')
                self.chat_area.insert(tk.END, f"You: {message}\n")
                self.chat_area.config(state='disabled')
                self.chat_area.yview(tk.END)
            self.message_input.delete(0, tk.END)

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message.startswith("[USER_LIST]"):
                    users = message[len("[USER_LIST]"):].split(',')
                    self.update_user_list(users)
                else:
                    self.chat_area.config(state='normal')
                    self.chat_area.insert(tk.END, message + '\n')
                    self.chat_area.config(state='disabled')
                    self.chat_area.yview(tk.END)
            except:
                self.chat_area.config(state='normal')
                self.chat_area.insert(tk.END, "[ERROR] Connection lost.\n")
                self.chat_area.config(state='disabled')
                self.client_socket.close()
                break

    def attach_image(self):
        image_path = filedialog.askopenfilename()
        if image_path:
            with open(image_path, 'rb') as img_file:
                img_data = img_file.read()
                self.client_socket.sendall(b'[IMAGE]' + img_data)

    def update_user_list(self, users):
        self.user_listbox.delete(0, tk.END)
        for user in users:
            self.user_listbox.insert(tk.END, user)

if __name__ == '__main__':
    root = tk.Tk()
    chat_client = ChatClient(root)
    root.mainloop()
