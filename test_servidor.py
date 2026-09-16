import sys
from socketTCP import SocketTCP

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python3 servidor_test.py <host> <puerto>")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])
    address = (host, port)

    print(f"Servidor iniciado. Escuchando en {address}...")

    server_socketTCP = SocketTCP()
    server_socketTCP.bind(address)
    connection_socketTCP, new_address = server_socketTCP.accept()

    print(f"¡Handshake Exitoso!")
    print(f"Nueva conexión establecida desde la dirección remota: {new_address}")
    print(f"El servidor asignó un nuevo socket en el puerto local: {connection_socketTCP.sock.getsockname()[1]}")