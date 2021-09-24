from typing import Dict, List
import json
import threading
import queue
import time
import datetime
import logging
import selectors
import multiprocessing
import io_connections
import debug_logger


def read_config_file(config: str) -> Dict:
    with open(config, "r") as f:
        return json.load(f)


def create_queues(count: int, logger: logging.Logger) -> List:
    queues: List[multiprocessing.Queue] = []
    for num in range(count):
        queues.append(multiprocessing.Queue(maxsize=1))
        logger.info(f"q{num} added to queue")
    return queues


def socket_server(
    settings: Dict,
    logger: logging.Logger,
    qs: List,
    command_q: queue.Queue,
    socket_control_q: queue.Queue,
) -> None:
    inputs = io_connections.get_connections(settings["inputs"], True, logger)
    sel = selectors.DefaultSelector()
    for conn in inputs:
        sel.register(
            fileobj=conn.sock, events=selectors.EVENT_READ, data=get_packets
        )
    while True:
        if not socket_control_q.empty():
            command = socket_control_q.get()
            if command == "start" or command == "stop":
                socket_control_q.put(command)
            else:
                # command is to close
                # drain all qs and break
                for idx, q in enumerate(qs):
                    # drain the q
                    while True:
                        try:
                            _ = q.get(block=False)
                            logger.debug(f"SHUTTING DOWN: q{idx} drained")
                        except queue.Empty:
                            break
                break
        events = sel.select(timeout=0)
        for key, mask in events:
            callback = key.data
            callback(
                key.fileobj,
                mask,
                settings,
                logger,
                qs,
                command_q,
                socket_control_q,
            )


def get_packets(
    sock,
    mask,
    settings: Dict,
    logger: logging.Logger,
    qs: List,
    command_q: queue.Queue,
    socket_control_q: queue.Queue,
) -> None:
    print("\n")
    data_packet, sensor_ip = sock.recvfrom(1024)
    sensor_port = sock.getsockname()[1]
    logger.info(
        f"data_packet from {sensor_ip} on port {sensor_port}: {data_packet}"
    )
    timestamp = datetime.datetime.now()
    data_packet = [timestamp, data_packet]

    # spin over all the inputs
    for idx, input in enumerate(settings["inputs"]):
        # check which sensor corresponds to the incoming packets

        if sensor_port == input["port"]:
            # load the sensors assigned queue
            q = qs[idx]

            # drain the q
            while True:
                try:
                    _ = q.get(block=False)
                except queue.Empty:
                    break
            # put new data in q
            q.put(data_packet, block=False)
            logger.debug(f"data put in q{idx}")

            if input["name"] == "controller":
                # logger.info(data_packet[1].decode())
                command_q.put(data_packet[1].decode())


def main() -> None:
    settings = read_config_file("config.json")
    debug_level = settings["debug_level"]
    log_length = settings["log_length"]
    log_length = datetime.timedelta(
        hours=int(log_length["hour"]),
        minutes=int(log_length["minute"]),
        seconds=int(log_length["second"]),
    )
    # logger_pass_queue = queue.Queue(maxsize=1)
    log_name = debug_logger.get_new_log_file_name("log", "debug", "log")
    logger = debug_logger.init_logger(__name__, debug_level, log_name)
    # logger_pass_queue.put(logger)
    qs = create_queues(len(settings["inputs"]), logger)
    command_q: queue.SimpleQueue = queue.SimpleQueue()
    socket_control_q: queue.SimpleQueue = queue.SimpleQueue()
    # video_control_q: queue.SimpleQueue = queue.SimpleQueue()
    server_thread = threading.Thread(
        name="socket_server",
        target=socket_server,
        args=(settings, logger, qs, command_q, socket_control_q),
    )
    server_thread.start()

    start_time = datetime.datetime.now()
    log = False

    while True:
        if not command_q.empty():
            command = command_q.get(block=False)
            logger.warning(f"COMMAND RECEIVED: {command}")

            if command == "start":
                log = True
                logger.warning(f"LOG_STATUS: {log}")
            elif command == "stop":
                log = False
                logger.warning(f"LOG_STATUS: {log}")
            elif command == "close":
                logger.warning(f"SHUTTING DOWN: {log}")
                socket_control_q.put(None)
                # video_control_q.put(None)
                break
            else:
                pass

        current_time = datetime.datetime.now()

        if current_time - start_time > log_length:
            log_name = debug_logger.get_new_log_file_name(
                "log", "debug", "log"
            )
            logger = debug_logger.update_handler(logger, log_name)
            logger.info(f"logger init {log_name}")
            start_time = current_time
        else:
            logger = logger

    server_thread.join()


if __name__ == "__main__":
    main()
