"""
Abstract base class that only hold lists containing the option names for configparser
"""

import configparser
import os

class FieldLists():
    """
    Abstract base class that only hold lists containing the option names for configparser
    """

    def __init__(self):
        self.task_fields = ["system_name",
                            "directory_path",
                            "delete_old_files",
                            "relocate_old_files",
                            "file_relocation_path",
                            "delete_when_relocation_is_full",
                            "disk_use_percent_warning_threshold",
                            "disk_use_percent_critical_threshold",
                            "last_access_threshold",
                            "email_users",
                            "bad_flag_percent"]

        self.db_fields = ["user_name",
                          "password",
                          "database",
                          "host",
                          "purge_database",
                          "purge_after_day_number"]

        self.thread_fields = ["thread_mode",
                              "thread_number"]

        self.email_fields = ["user_postfix",
                             "email_list"]

        self.task_config_file_name = os.path.expanduser("~/.dkmonitor/config/tasks.cfg")
        self.gen_config_file_name = os.path.expanduser("~/.dkmonitor/config/general.cfg")

        self.task_config = configparser.ConfigParser()
        self.gen_config = configparser.ConfigParser()


