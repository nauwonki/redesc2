import socket
import sys
from socketTCP import SocketTCP

def send_message(host, port):
    client_socket = SocketTCP()

    print(f"Connecting to {host}:{port}...")
    client_socket.connect((host, port))
    print("Connected.")

    message = sys.stdin.buffer.read()
    client_socket.send(message)
    print("Message sent.")
        
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python cliente.py <host> <port>")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])

    print("Client is running...")
    send_message(host, port)
