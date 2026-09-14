import socket
import sys
from socketTCP import SocketTCP

def send_message(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    message = sys.stdin.buffer.read()
    c = 16
    seq = 0
    chunks = [message[i:i+c] for i in range(0, len(message), c)]

    for id, chunk in enumerate(chunks):
        last = (id == len(chunks) - 1)
        segment = SocketTCP.create_segment(seq_num=seq, fin=last, payload=chunk)
        sock.sendto(segment, (host, port))
        seq = 1 - seq
        
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python cliente.py <host> <port>")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])

    print("Client is running...")
    send_message(host, port)
