"""
This script Is the main managing script for the dk_monitor script suite.
This script is indented to be run as a cron job to monitor actions on any
given disk or directory that is set by the adminstrator
"""

import threading
import argparse

import sys, os
sys.path.append(os.path.abspath(".."))
#sys.path.append(os.path.realpath(__file__)[:os.path.realpath(__file__).rfind("/")] + "/")

from dkmonitor.utilities.db_interface import DbEditor
from dkmonitor.utilities.dk_clean import DkClean
from dkmonitor.utilities import log_setup
from dkmonitor.config.config_reader import ConfigReader

from dkmonitor.emailer.dk_emailer import Emailer
from dkmonitor.stat.dk_stat import DkStat

class MonitorManager():
    """This class is the main managing class for all other classes
    It runs preset tasks that are found in the json settings file"""

    def __init__(self):
        #self.set_interface = SettingsInterface()
        #self.settings = self.set_interface.parse_and_check_all()
        config_reader = ConfigReader()
        self.settings = config_reader.configs_to_dict()

        self.logger = log_setup.setup_logger("monitor_log.log")

        #Configures Email api
        self.emailer = Emailer(self.settings["Email_Settings"]["user_postfix"])

        #Configures database
        self.database = DbEditor(self.settings["DataBase_Settings"]["database"],
                                 self.settings["DataBase_Settings"]["user_name"],
                                 self.settings["DataBase_Settings"]["password"],
                                 self.settings["DataBase_Settings"]["host"])

        if self.settings["DataBase_Settings"]["purge_database"] == "yes":
            self.logger.info("Cleaning Database")
            self.database.clean_data_base(self.settings["DataBase_Settings"]["purge_after_day_number"])

    def quick_scan(self, task):
        """
        Ment to be run hourly
        Checks use percent on a task
        if over quota, email users / clean disk if neccessary
        """

        #task = self.settings["Scheduled_Tasks"][task_name]
        dk_stat_obj = DkStat(system=task["System_Settings"]["system_name"], search_dir=task["System_Settings"]["directory_path"])

        disk_use = dk_stat_obj.get_disk_use_percent()
        if disk_use > task["Threshold_Settings"]["disk_use_percent_warning_threshold"]:
            dk_stat_obj.dir_search(task["Threshold_Settings"]["last_access_threshold"])
            dk_stat_obj.export_data(self.database)
            dk_stat_obj.email_users(self.settings["Email_Settings"]["user_postfix"], task, disk_use)

        if disk_use > task["Threshold_Settings"]["disk_use_percent_critical_threshold"]:
            self.clean_disk(task)

    def full_scan(self, task):
        """
        Performs full scan of directory by default
        logs disk statistics information in db
        if over quota, email users / clean disk if neccessary
        """

        #task = self.settings["Scheduled_Tasks"][task_name]
        dk_stat_obj = DkStat(system=task["System_Settings"]["system_name"],
                             search_dir=task["System_Settings"]["directory_path"])

        self.logger.info("Searching %s", task["System_Settings"]["directory_path"])
        dk_stat_obj.dir_search(task["Threshold_Settings"]["last_access_threshold"]) #Searches the Directory

        self.logger.info("Exporting %s data to database", task["System_Settings"]["directory_path"])
        dk_stat_obj.export_data(self.database) #Exports data from dk_stat_obj to the database

        self.logger.info("Emailing Users for %s", task["System_Settings"]["directory_path"])
        disk_use = dk_stat_obj.get_disk_use_percent()
        if disk_use > task["Threshold_Settings"]["disk_use_percent_warning_threshold"]:
            dk_stat_obj.email_users(self.settings["Email_Settings"]["user_postfix"], task, disk_use)

        if disk_use > task["Threshold_Settings"]["disk_use_percent_critical_threshold"]:
            self.clean_disk(task)


        self.logger.info("%s scan task complete", task["System_Settings"]["directory_path"])

    def clean_disk(self, task):
        """Cleaning routine function"""

        print("CLeaning Disk")

        self.logger.info("Cleaning %s", task["System_Settings"]["directory_path"])
        thread_settings = self.settings["Thread_Settings"]
        clean_obj = DkClean(task["System_Settings"]["directory_path"],
                            task["Scan_Settings"]["file_relocation_path"],
                            task["Threshold_Settings"]["last_access_threshold"])


        if task["Scan_Settings"]["relocate_old_files"] == "yes":
            if task["Scan_Settings"]["delete_when_relocation_is_full"] == "yes":
                if thread_settings["thread_mode"] == "yes":
                    clean_obj.move_all_threaded(thread_settings["thread_number"], delete_if_full=True)
                else:
                    clean_obj.move_all(delete_if_full=True)
            else:
                if thread_settings["thread_mode"] == "yes":
                    clean_obj.move_all_threaded(thread_settings["thread_number"])
                else:
                    clean_obj.move_all()

        elif task["Scan_Settings"]["delete_old_files"] == "yes":
            if thread_settings["thread_mode"] == "yes":
                clean_obj.delete_all_threaded(thread_settings["thread_number"])
            else:
                clean_obj.delete_all()

    @staticmethod
    def build_query_str(task):
        """Builds query string used to determine if disk needs to be cleaned"""

        query_str = "searched_directory = '{directory_path}' AND system = '{system_name}'"
        query_str = query_str.format(**task)
        return query_str


    def start_full_scans(self):
        """starts full scan on tasks"""

        print("Starting Full Scan")

        if self.settings["Thread_Settings"]["thread_mode"] == 'yes':
            for key, task in list(self.settings["Scheduled_Tasks"].items()):
                thread = threading.Thread(target=self.full_scan, args=(task,))
                thread.daemon = False
                thread.start()
        else:
            for key, task in list(self.settings["Scheduled_Tasks"].items()):
                self.full_scan(task)


    def start_quick_scans(self):
        """Starts quick scan on tasks"""

        print("Starting Quick Scan")

        if self.settings["Thread_Settings"]["thread_mode"] == "yes":
            for key, task in list(self.settings["Scheduled_Tasks"].items()):
                thread = threading.Thread(target=self.quick_scan, args=(task,))
                thread.daemon = False
                thread.start()
        else:
            for key, task in list(self.settings["Scheduled_Tasks"].items()):
                self.quick_scan(task)


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
                self.clean_disk(task)



def main():
    """Runs monitor_manager"""
    monitor = MonitorManager()
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("scan_type", help="Specify scan type: quick or full")
    args = parser.parse_args()
    if args.scan_type == "quick":
        monitor.start_quick_scans()
    elif args.scan_type == "full":
        monitor.start_full_scans()
    else:
        raise "Error: scan_type must be either 'full' or 'quick'"



if __name__ == "__main__":
    main()

