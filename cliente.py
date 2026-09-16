import socket
import sys
from socketTCP import SocketTCP

def send_message(host, port):
    client_socket = SocketTCP()

    print(f"Connecting to {host}:{port}...")
    client_socket.connect((host, port))
    print("Connected.")

    message = sys.stdin.buffer.read()
    c = 16
    seq = client_socket.seq_num
    chunks = [message[i:i+c] for i in range(0, len(message), c)]

    for id, chunk in enumerate(chunks):
        last = (id == len(chunks) - 1)
        segment = SocketTCP.create_segment(seq_num=seq, fin=last, payload=chunk)
        client_socket.sock.sendto(segment, client_socket.remote_address)
        seq = (1 - seq) % 256
        
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python cliente.py <host> <port>")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])

    print("Client is running...")
    send_message(host, port)
