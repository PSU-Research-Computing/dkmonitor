"""
File containing simple function that returns log object
"""

import os
import warnings
import logging
from logging import handlers


def setup_logger(log_file_path):
    """
    Takes log file name as input are returns a logger object
    TODO:
    """

    logger = logging.getLogger(log_file_path)
    logger.setLevel(logging.INFO)
    handler = handlers.RotatingFileHandler(log_file_path,
                                           maxBytes=1048576,
                                           backupCount=5)
    formatter = logging.Formatter(("%(asctime)s - %(name)s - "
                                   "%(levelname)s - %(message)s"))
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

