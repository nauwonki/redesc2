import socket 
import sys
from socketTCP import SocketTCP

def init_server(host, port):
    socket = SocketTCP()
    socket.bind((host, port))

    print(f"Server listening on {host}:{port}")

    connection_socket, client_addr = socket.accept()
    print(f"Accepted connection from {client_addr}")

    while True:
        message = b""
        while connection_socket.remaining_bytes > 0 or not message:
            chunk = connection_socket.recv(16)
            message += chunk
            if connection_socket.remaining_bytes == 0 and not connection_socket.leftover:
                break
        
        print(f"Received message from {client_addr}: {message.decode('utf-8')}")
                 
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python servidor.py <host> <port>")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])

    print("Server is running...")
    init_server(host, port)
