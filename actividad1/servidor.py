import socket 
import sys
import os
from socketTCP import SocketTCP
                 
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python servidor.py <host> <port>")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])
    debug = os.environ.get("DEBUG", "0") == "1"

    server_socket = SocketTCP(debug=debug)
    server_socket.bind((host, port))
    connection_socket, client_addr = server_socket.accept()

    message = b""
    while connection_socket.remaining_bytes > 0 or not message:
        chunk = connection_socket.recv(16)
        message += chunk
        if connection_socket.remaining_bytes == 0 and not connection_socket.leftover:
            break

    sys.stdout.buffer.write(message)
    connection_socket.recv_close()
        
    print(f"Received message from {client_addr}: {len(message)} bytes", file=sys.stderr)


