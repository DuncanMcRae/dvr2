import socket
import logging
import debug_logger


class Input_Connection:
    def __init__(self, name, host, port):
        self.name = name
        self.host = host
        # self.host = "0.0.0.0"
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # used so it can stop start without locking up the ports
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))


class Output_Connection:
    def __init__(self, name, host, port):
        self.name = name
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # used so it can stop start without locking up the ports
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


def main():
    # testing code
    logger = debug_logger.init_logger(__name__, "debug")
    first = Input_Connection("test", "0.0.0.0", 6666)


if __name__ == "__main__":
    main()
