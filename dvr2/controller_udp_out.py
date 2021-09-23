import argparse
import socket
import random
import datetime
import time
import sys

LISTENER = ("127.0.0.1", 20002)


class Connection:
    def __init__(self, name: str, host: str, port: int) -> None:
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
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # used so it can stop start without locking up the ports
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


def build_argparse() -> argparse.ArgumentParser:
    # Create the parser
    parser = argparse.ArgumentParser(
        prog="dvr_controller",
        description="send commands to dvr",
        epilog="SUPPORT: duncan.mcrae@sulmara.com",
        fromfile_prefix_chars="@",
    )
    # optional arguments start with '-' or '--'
    parser.add_argument("--version", action="version", version="%(prog) v2.0")
    # start recording
    parser.add_argument(
        "-s",
        "--start",
        action="store_true",
        help="start logging",
    )
    # stop recording
    parser.add_argument(
        "-x",
        "--stop",
        action="store_true",
        help="stop logging",
    )

    # close program
    parser.add_argument(
        "-c",
        "--close",
        action="store_true",
        help="close",
    )

    return parser


def send_control(connection: tuple, command: str) -> None:
    sock = Connection("control", LISTENER[0], LISTENER[1])
    sock.sock.sendto(command.encode(), connection)


def main(args) -> None:

    if len(sys.argv[:]) == 1:
        print("no command sent")

    if args.start:
        print("starting")
        send_control(LISTENER, "start")

    if args.stop:
        print("stopping")
        send_control(LISTENER, "stop")

    if args.close:
        print("close")
        send_control(LISTENER, "close")


if __name__ == "__main__":
    parser = build_argparse()
    # parse dem args
    args = parser.parse_args()
    print(f"ARGS: {args}")
    main(args)
