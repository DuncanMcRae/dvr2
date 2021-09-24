from typing import Dict, List
import json
import threading
import queue
import time
import datetime
import re
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


def socket_server(settings: Dict, logger: logging.Logger, qs: List) -> None:
    inputs = io_connections.get_connections(settings["inputs"], True, logger)
    sel = selectors.DefaultSelector()
    for conn in inputs:
        sel.register(
            fileobj=conn.sock, events=selectors.EVENT_READ, data=get_packets
        )
    while True:
        events = sel.select(timeout=0)
        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask, settings, logger, qs)


def get_packets(
    sock, mask, settings: Dict, logger: logging.Logger, qs: List
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

            # lock.acquire()
            # drain the q
            while True:
                try:
                    old = q.get(block=False)
                except queue.Empty:
                    break
            # put new data in q
            q.put(data_packet, block=False)
            logger.debug(f"data put in q{idx}")
            # lock.release()

            if (
                input["name"] == "controller"
                and data_packet[1].decode() == "close"
            ):
                logger.info("closing program")


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

    server_thread = threading.Thread(
        name="socket_server",
        target=socket_server,
        args=(settings, logger, qs),
    )
    server_thread.start()

    start_time = datetime.datetime.now()

    while True:
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

        # logger.info(datetime.datetime.now())
        # time.sleep(1)

    #     msg = log_queue.get()
    #     if msg == None:
    #         logger.warning("breaking")
    #         break
    #     else:
    #         logger.info(f"message rec {msg}")

    # server_thread.join()


if __name__ == "__main__":
    main()
