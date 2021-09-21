import argparse
import socket
import random
import datetime
import time
import sys

from socket_connections import Output_Connection

LISTENER = ("127.0.0.1", 6666)


def build_argparse():
    # Create the parser
    parser = argparse.ArgumentParser(
        prog="dvr_controller",
        description="send commands to dvr",
        epilog="SUPPORT: duncan.mcrae@sulmara.com",
        fromfile_prefix_chars="@",
    )
    # optional arguments start with '-' or '--'
    parser.add_argument("--version", action="version", version="%(prog) v2.0")
    # set a new folder
    parser.add_argument(
        "-s",
        "--start",
        action="store_true",
        help="start logging",
    )
    # set a new project
    parser.add_argument(
        "-x",
        "--stop",
        action="store_true",
        help="stop logging",
    )

    # parse dem args
    args = parser.parse_args()
    print(f"ARGS: {args}")
    return args


def send_control(connection: tuple, command: str):
    _sock = Output_Connection()
    _sock.sock.sendto(command.encode(), connection)


def main(args):
    if len(sys.argv[:]) == 1:
        print("no command sent")

    if args.start:
        print("starting")
        send_control(LISTENER, "start")

    if args.stop:
        print("stopping")
        send_control(LISTENER, "stop")


if __name__ == "__main__":
    args = build_argparse()
    main(args)
