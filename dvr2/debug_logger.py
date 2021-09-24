import logging
import time
from logging.handlers import TimedRotatingFileHandler
import datetime
from pathlib import Path


def get_new_log_file_name(folder: str, prefix: str, ext: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    folder = folder.replace(" ", "_")
    Path(folder).mkdir(parents=True, exist_ok=True)
    file_path = Path(folder)
    file_name = f"{prefix}_{timestamp}.{ext}".replace(" ", "_")
    file_name = file_path / file_name  # type: ignore
    return file_name


def init_logger(name: str, level: str, log_file_name: str) -> logging.Logger:

    logger = logging.getLogger(name)

    if level == "info":
        logger.setLevel(logging.INFO)

    if level == "debug":
        logger.setLevel(logging.DEBUG)

    if level == "warning":
        logger.setLevel(logging.WARNING)

    # set the format to include the timestamp
    formatter = logging.Formatter(
        "%(relativeCreated)7d,%(asctime)s,[%(levelname)s], NM:%(name)s, PID:%(processName)s, THR:%(threadName)s, MOD:%(module)s, MSG:%(message)s"
    )
    # print to file @ cwd
    file_handler = logging.FileHandler(log_file_name)
    # file_handler = TimedRotatingFileHandler(
    #     "log/debug.log", when="s", interval=10
    # )
    file_handler.setFormatter(formatter)
    # print to console
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


def update_handler(
    logger: logging.Logger, log_file_name: str
) -> logging.Logger:
    for handler in logger.handlers[:]:
        if isinstance(handler, logging.FileHandler):
            formatter = logger.handlers[0].formatter
            logger.removeHandler(handler)
            file_handler = logging.FileHandler(log_file_name)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
    return logger


if __name__ == "__main__":
    log_name = get_new_log_file_name("test/pr2", "debug", "log")
    logger = init_logger(__name__, "debug", log_name)

    LOG_LENGTH = datetime.timedelta(hours=0, minutes=0, seconds=10)
    start_time = datetime.datetime.now()
    while True:
        current_time = datetime.datetime.now()
        if current_time - start_time > LOG_LENGTH:
            log_name = get_new_log_file_name("test/pr2", "debug", "log")
            logger = init_logger(__name__, "debug", log_name)
            start_time = current_time
        else:
            logger = logger

        logger.info("before sleep")
        time.sleep(1)
        logger.warning("after sleep")
