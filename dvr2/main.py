import json
from multiprocessing import Process, Queue, Lock
import selectors
import datetime as dt

import debug_logger
import socket_connections


def read_json(filepath):
    print(filepath)
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
    cameras = []
    for camera in settings["cameras"]:
        cameras.append(
            socket_connections.Input_Connection(
                camera["name"], camera["ip"], camera["port"]
            )
        )
        logger.info(
            f"Camera connection created for {cameras[-1].name} @ {cameras[-1].host} on {cameras[-1].port}"
        )
    inputs = []
    for input in settings["inputs"]:
        inputs.append(
            socket_connections.Input_Connection(
                input["name"], input["ip"], input["port"]
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


def create_queues(_count, _logger):
    """the program is multi-processing, so needs a means to pass information
    from one CPU to another; queues are utilised here to do this.

    each queue has a maximum length of 1 so that it:
    -always has the latest information
    -can be checked to see if it is empty
    Args:
        _count (integer): the number of queues to make
        _logger (logging instance): for writing to the debug
    Returns:
        [list]: containing all the multi-processing queues
    """
    queues = []
    for num in range(_count):
        queues.append(Queue(maxsize=1))
        _logger.info(f"q{num} added to queue")
    return queues


def get_packets(sock, mask, lock, qs, settings, logger):
    """called when the selector registers a socket has data ready for reading,
    this method then grabs the byte data and puts it in to the correct queue

    Args:
        _sock (socket): the UDP connection (ip and port)
        _mask (int): not used (but 1 = EVENT_READ and 2 = EVENT_WRITE)
        _lock (multi-processing Lock): used to stop run-time errors happening when one process tries to get
        _qs (list): of the queues for passing between processes - one queue per input
        _settings (json object): package configuration file
        _logger (logging instance): for writing to the debug
    """
    data_packet, sensor_ip = sock.recvfrom(1024)
    sensor_port = sock.getsockname()[1]
    logger.info(
        f"data_packet from {sensor_ip} on port {sensor_port}: {data_packet}"
    )
    timestamp = dt.datetime.now()
    data_packet = [timestamp, data_packet]


def port_monitor(sel, lock, inputs, qs, settings, logger):
    """Infinite loop reacting when input sensor data hits the socket and is
    ready for reading. Callback get_packets method to check input verus configuration and place
    in to the correct queue.
    Args:
        _sel (selectors BaseSelector): used for monitoring the the incoming sockets
        _lock (multi-processing Lock): used to stop run-time errors happening when one process tries to get
        data from a queue that it thought was full, but the other process just emptied.
        _inputs (list): containing all the input socket connections
        _qs (list): of the queues for passing between processes - one queue per input
        _settings (json object): package configuration file
    """

    logger.info("port monitor called")

    for conn in inputs:
        sel.register(
            fileobj=conn.sock, events=selectors.EVENT_READ, data=get_packets
        )

    while True:
        events = sel.select(timeout=0)
        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask, lock, qs, settings, logger)


def main():
    # the multi-processing Lock stops run-time errors which occur when two processes
    # work on the smae object - like queues. With the lock, the processes have to wait
    # for the other process to be finished witht the queue
    lock = Lock()
    # initialise package variables
    settings = read_json("config.json")
    debug_level = settings["debug_level"]
    # initialises the debug logger
    logger = debug_logger.init_logger(__name__, debug_level)
    # gather all socket connections
    inputs, outputs = get_connections(settings, logger)
    # create queues that are used for io of socket data
    qs = create_queues(len(inputs), logger)
    # selectors are high-level efficient io multiplexing used to wait
    # for io readiness on multiple file objects
    sel = selectors.DefaultSelector()
    # spool up a process, one for input monitoring (main) The get the lock for control,
    # the list of socket connections for io, the queues for transfer of data
    # and the settings file for various io and driver purposes
    p1 = Process(
        target=port_monitor, args=(sel, lock, inputs, qs, settings, logger)
    )
    # generic multi-processing requirements - kill child processes when program loop is terminated
    p1.daemon = True
    p1.start()
    p1.join()


if __name__ == "__main__":
    main()
