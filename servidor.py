import socket 
import sys
from socketTCP import SocketTCP

def init_server(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))

    message = b""

    while True:
        segment, addr = sock.recvfrom(SocketTCP.buffer if False else 18)
        parsed_segment = SocketTCP.parse_segment(segment)

        print(f"Received segment from {addr}: {parsed_segment}")
        print(f"seq={parsed_segment['seq_num']}, syn={parsed_segment['syn']}, ack={parsed_segment['ack']}, fin={parsed_segment['fin']}, payload={parsed_segment['payload']}")

        message += parsed_segment['payload']

        if parsed_segment['fin']:
            print("Received FIN flag. Closing connection.")
            message = b""

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python servidor.py <host> <port>")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])

    print("Server is running...")
    init_server(host, port)
