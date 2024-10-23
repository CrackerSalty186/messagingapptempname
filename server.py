import socket
import threading
import keyboard  # type: ignore # Import the keyboard library

# Server setup
HOST = '127.0.0.1'  # Localhost for testing
PORT = 12345        # Port for the server

# Store all connected clients and their usernames
clients = {}
guest_count = 0  # To keep track of how many guest users are connected

# Function to handle each client
def handle_client(client_socket, addr):
    global guest_count

    # First message from the client should be the username
    username = client_socket.recv(1024).decode('utf-8')

    # If the username is "Guest", assign a unique number
    if username == "Guest":
        guest_count += 1
        username = f"Guest{guest_count}"

    clients[client_socket] = username
    print(f"[NEW CONNECTION] {username} connected.")

    # Broadcast updated user list
    broadcast_user_list()

    while True:
        try:
            # Receive message from the client
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print(f"[{username}] {message}")
                # Broadcast message with the username
                broadcast_message(f"{username}: {message}", client_socket)
            else:
                break
        except:
            break

    # When the client disconnects
    print(f"[DISCONNECTED] {username} disconnected.")
    client_socket.close()
    del clients[client_socket]
    
    # Broadcast updated user list
    broadcast_user_list()

# Broadcast message to all connected clients
def broadcast_message(message, client_socket):
    for client in clients:
        if client != client_socket:
            try:
                client.send(message.encode('utf-8'))
            except:
                client.close()
                del clients[client]

# Broadcast the user list to all clients
def broadcast_user_list():
    user_list = ",".join(clients.values())
    for client in clients:
        try:
            client.send(f"[USER_LIST]{user_list}".encode('utf-8'))
        except:
            client.close()
            del clients[client]

# Start the server and listen for connections
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"[SERVER STARTED] Listening on {HOST}:{PORT}")

    while True:
        client_socket, addr = server_socket.accept()
        # Start a new thread to handle the client
        thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

# Function to exit the server on keypress
def exit_on_keypress():
    print("Press 'q' to exit the server.")
    keyboard.wait('q')  # Wait for 'q' key press
    print("Exiting server...")
    exit()  # Exit the program

if __name__ == "__main__":
    # Start the exit listener in a separate thread
    threading.Thread(target=exit_on_keypress, daemon=True).start()
    
    # Start the server
    start_server()
