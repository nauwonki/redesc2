import socket
import sys
import os
import time
from socketTCP_copia import SocketTCP
        
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python cliente.py <host> <port>")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])
    debug = os.environ.get("DEBUG", "0") == "1"
    mode = os.environ.get("MODE", "go_back_n")
    use_cc = os.environ.get("CC", "0") == "1"
    timeout = float(os.environ.get("TIMEOUT", "1.0"))

    message = sys.stdin.buffer.read()
    print(f"Sending message to {host}:{port}: {len(message)} bytes", file=sys.stderr)
    if len(message) == 0:
        print("Warning: No data to send. The message is empty.", file=sys.stderr)

    print("Client is running...")
    client_socket = SocketTCP(debug=debug)
    client_socket.settimeout(timeout)
    client_socket.set_congestion_control(use_cc)
    client_socket.connect((host, port))
    t0 = time.time()
    client_socket.send(message, mode=mode)
    elapsed_time = time.time() - t0
    print(f"Message sent in {elapsed_time:.3f} seconds segments={client_socket.number_of_sent_segments}", file=sys.stderr)
    client_socket.close()