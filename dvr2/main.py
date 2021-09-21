import json

import debug_logger
import socket_connections


def read_json(filepath):
    with open(filepath, "r") as f:
        return json.load(f)


def get_connections(settings, logger):
    """creates all the UDP input and output UDP connections
    each connection is an instance of the classes pulled from the socket_connections module.
    Args:
        settings (json object): the loaded settings file
    Returns:
        [list]: creates two lists: input and output. Each list contains the UDP socket information
        each incoming sensor or output
    """
    debug_level = settings["debug_level"]
    inputs = []
    for camera in settings["inputs"]:
        inputs.append(
            socket_connections.Input_Connection(
                camera["name"], camera["ip"], camera["port"]
            )
        )
        logger.info(
            f"Input connection created for {inputs[-1].name} @ {inputs[-1].host} on {inputs[-1].port}"
        )
    outputs = []
    for output in settings["outputs"]:
        outputs.append(
            socket_connections.Output_Connection(
                output["name"], output["ip"], output["port"]
            )
        )
        logger.info(
            f"Output connection created to {outputs[-1].name} @ {outputs[-1].host} on {outputs[-1].port}"
        )
    return inputs, outputs


def main():
    # initialise package variables
    settings = read_json("config.json")
    debug_level = settings["debug_level"]
    # initialises the debug logger
    logger = debug_logger.init_logger(__name__, debug_level)
    inputs, outputs = get_connections(settings, logger)


if __name__ == "__main__":
    main()
