import logging
from logging import getLogger, StreamHandler, Logger, Formatter, NOTSET
from typing import Union, Optional


def remove_logger_root_handlers() -> None:
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)


def create_logger(name: Optional[str] = None, level: Union[str, int] = NOTSET) -> Logger:
    logger = getLogger(name)
    logger.setLevel(level)
    handler = StreamHandler()
    handler.setLevel(level)
    formatter = Formatter('[%(asctime)s] - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
