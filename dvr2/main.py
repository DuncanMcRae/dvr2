import json
from multiprocessing import Process, Queue, Lock
import multiprocessing
import threading
from queue import Empty
import selectors
import datetime as dt
import time

import debug_logger
import io_connections


def read_json(filepath):
    print(filepath)
    with open(filepath, "r") as f:
        return json.load(f)


def create_queues(count, logger):
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
    for num in range(count):
        queues.append(Queue(maxsize=1))
        logger.info(f"q{num} added to queue")
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

    # spin over all the inputs
    for idx, input in enumerate(settings["inputs"]):
        # check which sensor corresponds to the incoming packets

        if sensor_port == input["port"]:
            # load the sensors assigned queue
            q = qs[idx]

            lock.acquire()
            # drain the q
            while True:
                try:
                    old = q.get(block=False)
                except Empty:
                    break
            # put new data in q
            q.put(data_packet, block=False)
            logger.debug(f"data put in q{idx}")
            lock.release()

            if (
                input["name"] == "controller"
                and data_packet[1].decode() == "close"
            ):
                logger.info("closing program")


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


def get_camera_frames(logger, qs):
    while True:
        time.sleep(1)
        logger.info("cameras")


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
    inputs = io_connections.get_connections(settings["inputs"], True, logger)
    outputs = io_connections.get_connections(
        settings["outputs"], False, logger
    )
    cameras = io_connections.get_connections(
        settings["cameras"], False, logger
    )
    # create queues that are used for io of socket data
    qs = create_queues(len(inputs), logger)

    # selectors are high-level efficient io multiplexing used to wait
    # for io readiness on multiple file objects
    sel = selectors.DefaultSelector()
    # spool up a process, one for input monitoring (main) The get the lock for control,
    # the list of socket connections for io, the queues for transfer of data
    # and the settings file for various io and driver purposes
    # p1 = Process(
    #     target=port_monitor, args=(sel, lock, inputs, qs, settings, logger)
    # )

    p1 = Process(target=get_camera_frames, args=(logger, qs))
    # generic multi-processing requirements - kill child processes when program loop is terminated
    # p2 = Process(target=overlay_parser, args=(logger, qs))
    p1.daemon = True
    p1.start()

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

    # p1.join()


if __name__ == "__main__":
    multiprocessing.set_start_method("spawn")
    main()
