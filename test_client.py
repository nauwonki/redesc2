import sys
from socketTCP import SocketTCP
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python3 cliente_test.py <host> <puerto>")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])
    address = (host, port)

    print(f"Cliente iniciando conexión hacia {address}...")

    client_socketTCP = SocketTCP()
    client_socketTCP.connect(address)

    print(f"¡Handshake Exitoso!")
    print(f"El cliente se conectó al servidor en el endpoint: {client_socketTCP.remote_address}")