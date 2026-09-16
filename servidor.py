import socket 
import sys
from socketTCP import SocketTCP

def init_server(host, port):
    socket = SocketTCP()
    socket.bind((host, port))

    print(f"Server listening on {host}:{port}")

    connection_socket, client_addr = socket.accept()
    print(f"Accepted connection from {client_addr}")

    message = b""

    while True:
        segment, addr = connection_socket.sock.recvfrom(connection_socket.buffer)
        parsed_segment = SocketTCP.parse_segment(segment)

        print(f"Received segment from {addr}: {parsed_segment}")
        print(f"seq={parsed_segment['seq_num']}, payload={parsed_segment['payload']}")

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
