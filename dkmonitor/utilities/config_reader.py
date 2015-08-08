import psycopg2
import inspect

import sys, os
sys.path.append(os.path.abspath("../.."))

from dkmonitor.utilities.field_lists import FieldLists
from dkmonitor.utilities.log_setup import setup_logger

class ConfigReader():
    def __init__(self):
        self.logger = setup_logger("settings_log.log")
        try:
            self.config_root = os.environ["DKM_CONF"]
        except KeyError as err:
            self.logger.critical("No configuration files found, DKM_CONF not set")
            print("ERROR: ***No Configuration files found***")
            raise err

        print("yes")


    def read_tasks(self):
        pass

    def read_general(self):
        pass


if __name__ == "__main__":
    test = ConfigReader()
