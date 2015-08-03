"""
File containing simple function that returns log object
"""

import logging
import logging.handlers


def setup_logger(log_file_name):
    """Takes log file name as input are returns a logger object"""

    logger = logging.getLogger(log_file_name)
    logger.setLevel(logging.INFO)
    handler = logging.handlers.RotatingFileHandler(log_file_name, maxBytes=2048, backupCount=5)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


