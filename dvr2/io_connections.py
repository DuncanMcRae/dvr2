from typing import List, Dict
import logging
import json

import debug_logger
import socket_connections


def get_connections(
    setting: Dict, binding: bool, logger: logging.Logger
) -> List:
    """creates all the UDP input and output UDP connections
    each connection is an instance of the classes pulled from the socket_connections module.
    Args:
        settings (json object): the loaded settings file
    Returns:
        [list]: creates two lists: input and output. Each list contains the UDP socket information
        each incoming sensor or output
    """

    conn_list = []
    for conn in setting:
        conn_list.append(
            socket_connections.Connection(
                conn["name"], conn["ip"], conn["port"], logger
            )
        )
        if binding == True:
            conn_list[-1].bind_open()
    return conn_list


if __name__ == "__main__":
    # testing code
    logger = debug_logger.init_logger("my_logger", "debug")
    with open("config.json", "r") as f:
        settings = json.load(f)
    inputs = get_connections(settings["inputs"], True, logger)
    cameras = get_connections(settings["cameras"], False, logger)
    outputs = get_connections(settings["outputs"], False, logger)
