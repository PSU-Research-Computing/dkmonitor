"""
This script Is the main managing script for the dk_monitor script suite.
This script is indented to be run as a cron job to monitor actions on any
given disk or directory that is set by the adminstrator
"""

import threading

import sys
import os
sys.path.append(os.path.abspath(".."))

from dkmonitor.utilities.db_interface import DataBase
from dkmonitor.utilities.dk_clean import DkClean
from dkmonitor.utilities import log_setup
from dkmonitor.utilities.configurator_settings_obj import SettingsInterface

from dkmonitor.emailers.dk_emailer import Emailer
from dkmonitor.stat.dk_stat import DkStat

class MonitorManager():
    """This class is the main managing class for all other classes
    It runs preset tasks that are found in the json settings file"""

    def __init__(self):
        self.set_interface = SettingsInterface()
        self.settings = self.set_interface.parse_and_check_all()

        self.logger = log_setup.setup_logger("monitor_log.log")

        #Configures Email api
        self.emailer = Emailer(self.settings["Email_API"]["user_postfix"])

        #Configures database
        self.database = DataBase(self.settings["DataBase_info"]["database"],
                                 self.settings["DataBase_info"]["user_name"],
                                 self.settings["DataBase_info"]["password"],
                                 self.settings["DataBase_info"]["host"])

        if self.settings["DataBase_info"]["purge_database"] == "yes":
            self.logger.info("Cleaning Database")
            self.database.clean_data_base(self.settings["DataBase_info"]["purge_after_day_number"])

    def quick_scan(self, task_name):
        """
        Ment to be run hourly
        Checks use percent on a task
        if over quota, email users / clean disk if neccessary
        """

        task = self.settings["Scheduled_Tasks"][task_name]
        dk_stat_obj = DkStat(task["system_name"], task["directory_path"])

        disk_use = dk_stat_obj.get_disk_use_percent()
        if disk_use > task["disk_use_percent_warning_threshold"]:
            dk_stat_obj.dir_search()
            dk_stat_obj.export_data(self.database)
            dk_stat_obj.email_users(self.settings["Email_API"]["user_postfix"], task, disk_use)

        if disk_use > task["disk_use_percent_critical_threshold"]:
            self.clean_disk(task["directory_path"],
                            task["file_relocation_path"],
                            task["access_threshold"])

    def full_scan(self, task_name):
        """
        Performs full scan of directory by default
        logs disk statistics information in db
        if over quota, email users / clean disk if neccessary
        """

        task = self.settings["Scheduled_Tasks"][task_name]
        dk_stat_obj = DkStat(task["system_name"], task["directory_path"])

        self.logger.info("Searching %s", task["directory_path"])
        dk_stat_obj.dir_search() #Searches the Directory

        self.logger.info("Exporting %s data to database", task["directory_path"])
        dk_stat_obj.export_data(self.database) #Exports data from dk_stat_obj to the database

        self.logger.info("Emailing Users for %s", task["directory_path"])
        disk_use = dk_stat_obj.get_disk_use_percent()
        if disk_use > task["disk_use_warning_threshold"]:
            dk_stat_obj.email_users(self.settings["Email_API"]["user_postfix"], task, disk_use)

        if disk_use > task["disk_use_percent_critical_threshold"]:
            self.clean_disk(task["directory_path"],
                            task["file_relocation_path"],
                            task["access_threshold"])


        self.logger.info("%s scan task complete", task["directory_path"])


    def start(self):
        """starts all tasks"""

        if self.settings["Thread_Settings"]["thread_mode"] == 'yes':
            self.run_tasks_threading()
        else:
            self.run_tasks()

    def run_full_scans(self):
        """Runs all tasks in the json settings file"""

        for task in self.settings["Scheduled_Tasks"].keys():
            self.full_scan(task)

    def run_full_scan_threading(self):
        """Runs all tasks in the json settings file with multiple threads"""

        for task in self.settings["Scheduled_Tasks"].keys():
            thread = threading.Thread(target=self.full_scan, args=(task,))
            thread.daemon = False
            thread.start()

    def run_quick_scans(self):
        """Runs all tasks in the json settings file"""

        for task in self.settings["Scheduled_Tasks"].keys():
            self.quick_scan(task)

    def run_quick_scan_threading(self):
        """Runs all tasks in the json settings file with multiple threads"""

        for task in self.settings["Scheduled_Tasks"].keys():
            thread = threading.Thread(target=self.quick_scan, args=(task,))
            thread.daemon = False
            thread.start()

    def check_clean_task(self, task):
        """
        Checks if directory needs to be cleaned
        Starts cleaning routine if flagged
        """

        if task["relocate_old_files"] == "yes":
            query_str = self.build_query_str(task)
            collumn_names = "disk_use_percent"

            query_data = self.database.query_date_compare("directory_stats",
                                                          query_str,
                                                          collumn_names)
            if query_data == None:
                pass
            elif query_data[0] > task["disk_use_percent_threshold"]:
                self.clean_disk(task["directory_path"],
                                task["file_relocation_path"],
                                task["last_access_threshold"])

    def clean_disk(self, directory, relocation_path, access_threshold):
        """Cleaning routine function"""

        print("CLeaning...")
        self.logger.info("Cleaning %s", directory)
        thread_settings = self.settings["Thread_Settings"]
        clean_obj = DkClean(directory, relocation_path, access_threshold)
        if thread_settings["thread_mode"] == "yes":
            clean_obj.move_all_threaded(thread_settings["thread_number"])
        else:
            clean_obj.move_all()


    @staticmethod
    def build_query_str(task):
        """Builds query string used to determine if disk needs to be cleaned"""

        query_str = "searched_directory = '{directory_path}' AND system = '{system_name}'"
        query_str = query_str.format(**task)
        return query_str

def main():
    """Runs monitor_manager"""
    monitor = MonitorManager()
    monitor.start()


if __name__ == "__main__":
    main()

