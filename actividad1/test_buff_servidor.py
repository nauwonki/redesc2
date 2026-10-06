import sys
import os
from redesc2.actividad1.socketTCP import SocketTCP

if __name__ == "__main__":
    host, port = sys.argv[1], int(sys.argv[2])
    debug = os.environ.get("DEBUG", "0") == "1"

    server = SocketTCP(debug=debug)
    server.bind((host, port))
    conn, addr = server.accept()

    n = 25  
    part1 = conn.recv(n)
    part2 = conn.recv(n)

    full = part1 + part2
    print(f"part1 ({len(part1)} bytes): {part1}")
    print(f"part2 ({len(part2)} bytes): {part2}")
    print(f"total: {full}")
    assert len(part1) == n and len(part2) == n, "recv no respeto buff_size exacto"
    print("recv(buff_size) con n no multiplo de 16: PASSED")

    conn.recv_close()