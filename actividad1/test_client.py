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

    # test 1
    message = "Mensje de len=16".encode()
    client_socketTCP.send(message)
    # test 2
    message = "Mensaje de largo 19".encode()
    client_socketTCP.send(message)
    # test 3
    message = "Mensaje de largo 19".encode()
    client_socketTCP.send(message)

    client_socketTCP.close()
    print(f"Cliente cerró la conexión con el servidor.")

    print(f"¡Handshake Exitoso!")
