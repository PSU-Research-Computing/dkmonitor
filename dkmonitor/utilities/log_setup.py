"""
File containing simple function that returns log object
"""

import os
import logging, logging.handlers

def setup_logger(log_file_name):
    """
    Takes log file name as input are returns a logger object
    TODO:
        Replace print warnings with warnings library
    """
    try:
        log_path = os.environ["DKM_LOG"]
    except KeyError:
        print("ERROR: ***Could Not find log storage directory***")
        print("Logging to current working directory")
        log_path = os.path.abspath(".")

    if not os.path.exists(log_path):
        print("ERROR: The path specified in DKM_LOG does not exist")
        print("Logging to current working directory")
        log_path = os.path.abspath(".")
    if os.path.isfile(log_path):
        print("ERROR: The path specifed in DKM_LOG points to a file")
        print("Logging to current working directory")
        log_path = os.path.abspath(".")

    log_path = os.path.join(log_path, '{}.log'.format(log_file_name))
    logger = logging.getLogger(log_path)
    logger.setLevel(logging.INFO)
    handler = logging.handlers.RotatingFileHandler(log_path,
                                                   maxBytes=1048576,
                                                   backupCount=5)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

