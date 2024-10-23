import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog
from tkinter import ttk

# Client setup
HOST = '127.0.0.1'  # Same host as the server
PORT = 12345        # Same port as the server

class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Client")

        # Prompt the user for a username
        self.username = simpledialog.askstring("Username", "Enter your username", parent=self.root)
        if not self.username:
            self.username = "Guest"  # Default username if none provided

        # Setup socket for communication
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((HOST, PORT))
        self.client_socket.send(self.username.encode('utf-8'))  # Send the username to the server

        # Start a thread to listen for incoming messages and user updates
        threading.Thread(target=self.receive_messages, daemon=True).start()

        # Main layout for the chat interface
        self.chat_area = scrolledtext.ScrolledText(self.root, state='disabled', wrap=tk.WORD)
        self.chat_area.pack(padx=10, pady=10, side=tk.LEFT)

        # Emoji Picker
        self.emoji_var = tk.StringVar()
        emoji_label = tk.Label(self.root, text="Select Emoji:")
        emoji_label.pack(padx=10, pady=(0, 5))
        
        emoji_options = ["😀", "😂", "😍", "😎", "😭", "😡", "👍", "🙌", "🔥", "✨", "🎉"]
        self.emoji_picker = ttk.Combobox(self.root, textvariable=self.emoji_var, values=emoji_options, state='readonly')
        self.emoji_picker.pack(padx=10, pady=(0, 5))
        self.emoji_picker.bind("<<ComboboxSelected>>", self.add_emoji)

        # Input box for typing messages
        self.message_input = tk.Entry(self.root, width=50)
        self.message_input.pack(padx=10, pady=(0, 10))
        self.message_input.bind("<Return>", self.send_message)

        # Send button to send the message to the server
        send_button = tk.Button(self.root, text="Send", command=self.send_message)
        send_button.pack(pady=(0, 10))

        # User List
        self.user_listbox = tk.Listbox(self.root, height=10)
        self.user_listbox.pack(padx=10, pady=10, side=tk.RIGHT)

    def add_emoji(self, event=None):
        """Add the selected emoji to the message input box."""
        emoji = self.emoji_var.get()
        self.message_input.insert(tk.END, emoji)

    # Method to send messages to the server
    def send_message(self, event=None):
        message = self.message_input.get()
        if message:
            self.client_socket.send(message.encode('utf-8'))
            self.message_input.delete(0, tk.END)  # Clear the input after sending

            # Show the user's own message in the chat area
            self.chat_area.config(state='normal')
            self.chat_area.insert(tk.END, f"You: {message}\n")
            self.chat_area.config(state='disabled')
            self.chat_area.yview(tk.END)  # Scroll to the end

    # Method to receive messages and user updates from the server
    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if message.startswith("[USER_LIST]"):
                    # Update the user list
                    users = message[len("[USER_LIST]"):].split(',')
                    self.update_user_list(users)
                else:
                    # Update the chat area with the received message
                    self.chat_area.config(state='normal')
                    self.chat_area.insert(tk.END, message + '\n')
                    self.chat_area.config(state='disabled')
                    self.chat_area.yview(tk.END)  # Scroll to the end
            except:
                # Handle disconnection from the server
                self.chat_area.config(state='normal')
                self.chat_area.insert(tk.END, "[ERROR] Connection lost.\n")
                self.chat_area.config(state='disabled')
                self.client_socket.close()
                break

    # Update the user list in the UI
    def update_user_list(self, users):
        self.user_listbox.delete(0, tk.END)
        for user in users:
            self.user_listbox.insert(tk.END, user)

if __name__ == '__main__':
    root = tk.Tk()
    chat_client = ChatClient(root)
    root.mainloop()
