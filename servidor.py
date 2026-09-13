import socket 
import sys

def init_server(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))

    while True:
        data, addr = sock.recvfrom(16)
        print(f"Received message: {data.decode()} from {addr}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python servidor.py <host> <port>")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])

    print("Server is running...")
    init_server(host, port)
