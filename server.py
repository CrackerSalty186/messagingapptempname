import socket
import threading

# Server setup
HOST = '127.0.0.1'  
PORT = 12345        

clients = {}
guest_count = 0  

def handle_client(client_socket, addr):
    global guest_count

    username = client_socket.recv(1024).decode('utf-8')
    if username == "Guest":
        guest_count += 1
        username = f"Guest{guest_count}"

    clients[client_socket] = username
    print(f"[NEW CONNECTION] {username} connected.")
    broadcast_user_list()

    while True:
        try:
            message = client_socket.recv(1024)
            if message:
                if message.decode('utf-8').startswith("/dm"):
                    handle_dm(client_socket, message.decode('utf-8'))
                else:
                    print(f"[{username}] {message.decode('utf-8')}")
                    broadcast_message(f"{username}: {message.decode('utf-8')}", client_socket)
            else:
                break
        except:
            break

    print(f"[DISCONNECTED] {username} disconnected.")
    client_socket.close()
    del clients[client_socket]
    broadcast_user_list()

def handle_dm(sender_socket, message):
    _, recipient_name, dm_message = message.split(" ", 2)
    recipient_socket = None
    for client, name in clients.items():
        if name == recipient_name:
            recipient_socket = client
            break

    if recipient_socket:
        sender_name = clients[sender_socket]
        try:
            recipient_socket.send(f"[DM from {sender_name}]: {dm_message}".encode('utf-8'))
        except:
            recipient_socket.close()
            del clients[recipient_socket]

def broadcast_message(message, client_socket):
    for client in clients:
        if client != client_socket:
            try:
                client.send(message.encode('utf-8'))
            except:
                client.close()
                del clients[client]

def broadcast_user_list():
    user_list = ",".join(clients.values())
    for client in clients:
        try:
            client.send(f"[USER_LIST]{user_list}".encode('utf-8'))
        except:
            client.close()
            del clients[client]

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"[SERVER STARTED] Listening on {HOST}:{PORT}")

    while True:
        client_socket, addr = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    start_server()
