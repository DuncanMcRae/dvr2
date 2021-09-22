import socket
import logging
import debug_logger


class Connection:
    def __init__(
        self, name: str, host: str, port: int, logger: logging.Logger
    ) -> None:
        """[creates a UDP socket connection either input (with bind) or output]

        Args:
            name (str): [name of connection]
            host (str): [ip address 'X.X.X.X']
            port (int): [port number >1500]
            logger (logging.Logger): [the logger for debug_logging]
        """
        self.name = name
        self.host = host
        self.port = port
        self.logger = logger
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # used so it can stop start without locking up the ports
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        logger.info(
            f"Connection made to {self.name} @ {self.host}:{self.port}"
        )

    def bind_open(self):
        self.sock.bind((self.host, self.port))
        self.logger.info(f"Port {self.port} open")


def main():
    # testing code
    logger = debug_logger.init_logger("my_logger", "debug")
    first = Connection("test", "0.0.0.0", 6666, logger)
    first.bind_open()


if __name__ == "__main__":
    main()
