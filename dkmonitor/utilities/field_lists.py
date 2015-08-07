"""
Abstract base class that only hold lists containing the option names for configparser
"""

import configparser
import os
import collections

class FieldLists():
    """
    Abstract base class that only hold lists containing the option names for configparser
    """

    def __init__(self):
        self.task_fields = collections.OrderedDict()
        self.task_fields["System_Settings"] = ["system_name", "directory_path"]
        self.task_fields["Scan_Settings"] = ["delete_old_files",
                                             "relocate_old_files",
                                             "file_relocation_path",
                                             "delete_when_relocation_is_full"]
        self.task_fields["Threshold_Settings"] = ["disk_use_percent_warning_threshold",
                                                  "disk_use_percent_critical_threshold",
                                                  "last_access_threshold"]
        self.task_fields["Email_Settings"] = ["email_usage_warnings",
                                              "email_data_alteration_notices",
                                              "bad_flag_percent"]

        self.general_fields = collections.OrderedDict()
        self.general_fields["DataBase_Settings"] = ["user_name",
                                                    "password",
                                                    "database",
                                                    "host",
                                                    "purge_database",
                                                    "purge_after_day_number"]
        self.general_fields["Thread_Settings"] = ["thread_mode", "thread_number"]
        self.general_fields["Email_Settings"] = ["user_postfix", "email_list"]

        self.task_config_file_name = os.path.expanduser("~/.dkmonitor/config/tasks/tasks_tmp.cfg")
        self.gen_config_file_name = os.path.expanduser("~/.dkmonitor/config/general.cfg")

        self.task_config = configparser.ConfigParser()
        self.gen_config = configparser.ConfigParser()


