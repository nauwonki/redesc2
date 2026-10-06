import sys
import os
from redesc2.actividad1.socketTCP import SocketTCP

if __name__ == "__main__":
    host, port = sys.argv[1], int(sys.argv[2])
    debug = os.environ.get("DEBUG", "0") == "1"

    n = 25
    message = bytes(range(2 * n))  

    client = SocketTCP(debug=debug)
    client.connect((host, port))
    client.send(message)
    client.close()