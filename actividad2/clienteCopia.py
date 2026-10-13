import socket
import sys
import os
from socketTCP_copia import SocketTCP
        
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python cliente.py <host> <port>")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])
    debug = os.environ.get("DEBUG", "0") == "1"

    message = sys.stdin.buffer.read()
    print(f"Sending message to {host}:{port}: {len(message)} bytes", file=sys.stderr)
    if len(message) == 0:
        print("Warning: No data to send. The message is empty.", file=sys.stderr)

    print("Client is running...")
    client_socket = SocketTCP(debug=debug)
    client_socket.connect((host, port))
    client_socket.send(message, mode="go_back_n")
    client_socket.close()