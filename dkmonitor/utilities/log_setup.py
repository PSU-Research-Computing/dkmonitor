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
        Replace print warnings with warnings library
        Move DKM_LOG abstraction outside of setup_logger
    """
    log_dir = os.path.expanduser(os.path.basename(log_file_path))
    if os.path.isdir() and os.access(DEFAULT_LOG_PATH, os.R_OK):
        continue
    elif os.path.isdir(DEFAULT_LOG_PATH) and os.access(DEFAULT_LOG_PATH, os.R_OK):
        log_path = DEFAULT_LOG_PATH
    else:
        warnings.warn(("Could Not find log storage directory, Logging to"
                       "current working directory"))
        log_path = os.path.abspath(".")

    log_file_path = os.path.join(log_path, log_file_name)
    logger = logging.getLogger(log_path)
    logger.setLevel(logging.INFO)
    handler = handlers.RotatingFileHandler(log_path,
                                           maxBytes=1048576,
                                           backupCount=5)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

