import socket_connections


def main():
    conn = socket_connections.Input_Connection("0.0.0.0", 6666)

    while True:
        data_packet = conn.sock.recv(1024)
        print(data_packet.decode())


if __name__ == "__main__":
    main()
