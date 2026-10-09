import sys
from socketTCP_copia import SocketTCP

if __name__ == "__main__":
    address = (sys.argv[1], int(sys.argv[2]))

    client_socketTCP = SocketTCP(debug=True)
    client_socketTCP.connect(address)

    client_socketTCP.send("Mensje de len=16".encode(), mode="go_back_n")      # test 1
    client_socketTCP.send("Mensaje de largo 19".encode(), mode="go_back_n")   # test 2
    client_socketTCP.send("Mensaje de largo 19".encode(), mode="go_back_n")   # test 3

    client_socketTCP.close()