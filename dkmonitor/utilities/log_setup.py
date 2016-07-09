"""
File containing simple function that returns log object
"""

import os
import warnings
import logging
from logging import handlers

FIRST_CHOICE = '/var/log/dkmonitor'
SECOND_CHOICE = os.path.expanduser('~/.dkmonitor/log')

def setup_logger(log_file_name):
    """
    Takes log file name as input are returns a logger object
    TODO:
        Replace print warnings with warnings library
        Move DKM_LOG abstraction outside of setup_logger
    """
    if os.path.isdir(FIRST_CHOICE) and os.access(FIRST_CHOICE, os.R_OK):
        log_path = os.path.join(FIRST_CHOICE, log_file_name)
    elif os.path.isdir(SECOND_CHOICE) and os.access(SECOND_CHOICE, os.R_OK):
        log_path = os.path.join(SECOND_CHOICE, log_file_name)
    else:
        warnings.warn(("Could Not find log storage directory, Logging to"
                       "current working directory"))
        log_path = os.path.join(os.path.abspath("."), log_file_name)

    log_path = os.path.join(log_path, '{}.log'.format(log_file_name))
    logger = logging.getLogger(log_path)
    logger.setLevel(logging.INFO)
    handler = handlers.RotatingFileHandler(log_path,
                                           maxBytes=1048576,
                                           backupCount=5)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

