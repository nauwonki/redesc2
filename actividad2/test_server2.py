import sys
from socketTCP_copia import SocketTCP

if __name__ == "__main__":
    address = (sys.argv[1], int(sys.argv[2]))

    server_socketTCP = SocketTCP(debug=True)
    server_socketTCP.bind(address)
    connection_socketTCP, new_address = server_socketTCP.accept()

    # test 1
    buff_size = 16
    full_message = connection_socketTCP.recv(buff_size, mode="go_back_n")
    print("Test 1 received:", full_message)
    print("Test 1: Passed" if full_message == "Mensje de len=16".encode() else "Test 1: Failed")

    # test 2
    buff_size = 19
    full_message = connection_socketTCP.recv(buff_size, mode="go_back_n")
    print("Test 2 received:", full_message)
    print("Test 2: Passed" if full_message == "Mensaje de largo 19".encode() else "Test 2: Failed")

    # test 3
    buff_size = 14
    message_part_1 = connection_socketTCP.recv(buff_size, mode="go_back_n")
    message_part_2 = connection_socketTCP.recv(buff_size, mode="go_back_n")
    print("Test 3 received:", message_part_1 + message_part_2)
    print("Test 3: Passed" if (message_part_1 + message_part_2) == "Mensaje de largo 19".encode() else "Test 3: Failed")

    connection_socketTCP.recv_close()