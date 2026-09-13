import socket
import sys

def send_message(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    message = sys.stdin.buffer.read()
    c = 16
    for i in range(0, len(message), c):
        chunk = message[i:i+c]
        sock.sendto(chunk, (host, port))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python cliente.py <host> <port>")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])

    print("Client is running...")
    send_message(host, port)
