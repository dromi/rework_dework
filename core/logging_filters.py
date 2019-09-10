import logging
import sys
from logging.handlers import TimedRotatingFileHandler


class InfoFilter(logging.Filter):
    def filter(self, rec):
        return rec.levelno in (logging.DEBUG, logging.INFO)


class ErrorFilter(logging.Filter):
    def filter(self, rec):
        return rec.levelno in (logging.WARNING, logging.ERROR, logging.CRITICAL)


def create_logger(logging_path, logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    h1 = logging.StreamHandler(sys.stdout)
    h1.setLevel(logging.DEBUG)
    h1.addFilter(InfoFilter())
    h1.setFormatter(formatter)
    logger.addHandler(h1)

    h2 = logging.StreamHandler(sys.stderr)
    h2.setLevel(logging.WARNING)
    h2.addFilter(ErrorFilter())
    h2.setFormatter(formatter)
    logger.addHandler(h2)

    h3 = TimedRotatingFileHandler(logging_path, when="midnight", interval=1)
    h3.setLevel(logging.DEBUG)
    h3.setFormatter(formatter)
    logger.addHandler(h3)

    return logger
