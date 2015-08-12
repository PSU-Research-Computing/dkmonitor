import psycopg2
import inspect
import configparser

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

        self.task_config = configparser.ConfigParser()
        self.gen_config = configparser.ConfigParser()

    #Task settings file(s) read functions
    def read_tasks(self):
        task_root = self.config_root + "/tasks/"
        try:
            task_files = os.listdir(task_root)
        except OSError as err:
            self.logger.critical("No tasks directory found in DKM_CONF")
            raise err

        for task_file in task_files:
            task_file = task_root + task_file
            self.read_task(task_file)

    def read_task(self, task_file):
        self.task_config.read(task_file)


    def read_system_settings(self):
        pass

    def read_scan_settings(self):
        pass

    def read_threshold_settings(self):
        pass

    def read_task_email_settings(self):
        pass

    #General settings file read functions
    def read_general(self):
        pass

    def read_db_settings(self):
        pass

    def read_thread_settings(self):
        pass

    def read_general_email_settings(self):
        pass


if __name__ == "__main__":
    test = ConfigReader()
