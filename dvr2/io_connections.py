from typing import List, Dict
import logging
import json

import debug_logger
import socket_connections


def get_connections(
    setting: Dict, binding: bool, logger: logging.Logger
) -> List:

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
    logger = debug_logger.init_logger("my_logger", "debug", "debug.log")
    with open("config.json", "r") as f:
        settings = json.load(f)
    inputs = get_connections(settings["inputs"], True, logger)
    cameras = get_connections(settings["cameras"], False, logger)
    outputs = get_connections(settings["outputs"], False, logger)
