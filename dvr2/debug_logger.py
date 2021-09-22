import logging
import time


def init_logger(name: str, level: str) -> logging.Logger:
    """[generates a logger that logs in a specific format to ./debug.log]

    Args:
        name (str): [name of logger]
        level (str): [debug level]

    Returns:
        logging.Logger: [the logger all ready to go]
    """
    logger = logging.getLogger(name)

    if level == "info":
        logger.setLevel(logging.INFO)

    if level == "debug":
        logger.setLevel(logging.DEBUG)

    if level == "warning":
        logger.setLevel(logging.WARNING)

    # set the format to include the timestamp
    formatter = logging.Formatter(
        "%(relativeCreated)7d,%(asctime)s,%(levelname)-8s,PID:%(process)s, THR:%(threadName)s, MOD:%(module)s, MSG:%(message)s"
    )
    # print to file @ cwd
    file_handler = logging.FileHandler("debug.log")
    file_handler.setFormatter(formatter)
    # print to console
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.info("logger initiated: cwd/debug.log")
    return logger


if __name__ == "__main__":
    logger = init_logger("my_logger", "debug")
    logger.info("before sleep")
    time.sleep(1)
    logger.warning("after sleep")
