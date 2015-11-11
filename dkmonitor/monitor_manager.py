"""
This script Is the main managing script for the dk_monitor script suite.
This script is indented to be run as a cron job to monitor actions on any
given disk or directory that is set by the adminstrator
"""

import threading
import argparse
import socket

import sys, os
sys.path.append(os.path.abspath(".."))

#from dkmonitor.utilities.db_interface import DbEditor
from dkmonitor.utilities.new_db_int import DataBase
from dkmonitor.utilities.dk_clean import DkClean
from dkmonitor.utilities import log_setup
from dkmonitor.config.config_reader import ConfigReader

from dkmonitor.config.settings_manager import export_settings()
from dkmonitor.config.task_manager import export_tasks()

from dkmonitor.stat.dk_stat import DkStat

class MonitorManager():
    """This class is the main managing class for all other classes
    It runs preset tasks that are found in the json settings file"""

    def __init__(self):
        #config_reader = ConfigReader()
        #self.settings = config_reader.configs_to_dict()
        self.settings = export_settings()
        self.tasks = export_tasks()

        self.logger = log_setup.setup_logger(__name__)

        #Configures database
        """
        self.database = DbEditor(host_name=self.settings["DataBase_Settings"]["host"],
                                 database=self.settings["DataBase_Settings"]["database"],
                                 user_name=self.settings["DataBase_Settings"]["user_name"],
                                 password=self.settings["DataBase_Settings"]["password"])
         """
        self.database = DataBase(hostname=self.settings["DataBase_Settings"]["host"],
                                 username=self.settings["DataBase_Settings"]["user_name"],
                                 password=self.settings["DataBase_Settings"]["password"],
                                 database=self.settings["DataBase_Settings"]["database"])

        if self.settings["DataBase_Settings"]["purge_database"] == "yes":
            self.logger.info("Cleaning Database")
            #self.database.clean_data_base(self.settings["DataBase_Settings"]["purge_after_day_number"])

    def quick_scan(self, task):
        """
        Ment to be run hourly
        Checks use percent on a task
        if over quota, email users / clean disk if neccessary
        """

        dk_stat_obj = DkStat(system=task["hostname"],
                             search_dir=task["target_path"])

        disk_use = dk_stat_obj.get_disk_use_percent()
        if disk_use > task["usage_warning_threshold"]:
            dk_stat_obj.dir_search(task["old_file_threshold"])
            dk_stat_obj.export_data(self.database)
            #dk_stat_obj.email_users(self.settings["Email_Settings"]["user_postfix"], task, disk_use)

        if disk_use > task["usage_critical_threshold"]:
            self.clean_disk(task)

    def full_scan(self, task):
        """
        Performs full scan of directory by default
        logs disk statistics information in db
        if over quota, email users / clean disk if neccessary
        """

        try:
            dk_stat_obj = DkStat(system=task["hostname"],
                                 search_dir=task["target_path"])

            self.logger.info("Searching %s", task["target_path"])
            dk_stat_obj.dir_search(task["old_file_threshold"]) #Searches the Directory

            self.logger.info("Exporting %s data to database", task["target_path"])
            #dk_stat_obj.export_data(self.database) #Exports data from dk_stat_obj to the database
            self.database.store_rows(dk_stat_obj.export_rows())

            self.logger.info("Emailing Users for %s", task["target_path"])
            disk_use = dk_stat_obj.get_disk_use_percent()
            if disk_use > task["usage_warning_threshold"]:
                #dk_stat_obj.email_users(self.settings["Email_Settings"]["user_postfix"], task, disk_use)
                pass

            if disk_use > task["usage_critical_threshold"]:
                self.clean_disk(task)


            self.logger.info("%s scan task complete", task["target_path"])
        except PermissionError:
            print("You do not have permission to {}".format(task["target_path"]))
        except OSError:
            print("There is no directory: {}".format(task["target_path"]))

    def clean_disk(self, task):
        """Cleaning routine function"""

        print("CLeaning Disk")

        self.logger.info("Cleaning %s", task["target_path"])
        thread_settings = self.settings["Thread_Settings"]
        clean_obj = DkClean(search_dir=task["target_path"],
                            move_to=task["relocation_path"],
                            access_threshold=task["old_file_threshold"],
                            host_name=task["hostname"])


        if task["relocation_path"] != None:
            if task["delete_when_full"] is True:
                if thread_settings["thread_mode"] == "yes":
                    clean_obj.move_all_threaded(thread_settings["thread_number"], delete_if_full=True)
                else:
                    clean_obj.move_all(delete_if_full=True)
            else:
                if thread_settings["thread_mode"] == "yes":
                    clean_obj.move_all_threaded(thread_settings["thread_number"])
                else:
                    clean_obj.move_all()

        elif task["delete_old_files"] is True:
            if thread_settings["thread_mode"] == "yes":
                clean_obj.delete_all_threaded(thread_settings["thread_number"])
            else:
                clean_obj.delete_all()

    @staticmethod
    def build_query_str(task):
        """Builds query string used to determine if disk needs to be cleaned"""

        query_str = "searched_directory = '{directory_path}' AND system = '{system_host_name}'"
        query_str = query_str.format(**task)
        return query_str


    def start_full_scans(self):
        """starts full scan on tasks"""

        print("Starting Full Scan")

        for key, task in list(self.tasks].items()):
            if self.check_host_name(task) is True:
                if self.settings["Thread_Settings"]["thread_mode"] == "yes":
                    thread = threading.Thread(target=self.full_scan, args=(task,))
                    thread.daemon = False
                    thread.start()
                else:
                    self.full_scan(task)


    def start_quick_scans(self):
        """Starts quick scan on tasks"""

        print("Starting Quick Scan")

        for key, task in list(self.tasks.items()):
            if self.check_host_name(task) is True:
                if self.settings["Thread_Settings"]["thread_mode"] == "yes":
                    thread = threading.Thread(target=self.quick_scan, args=(task,))
                    thread.daemon = False
                    thread.start()
                else:
                    self.quick_scan(task)

    def check_clean_task(self, task):
        """
        Checks if directory needs to be cleaned
        Starts cleaning routine if flagged

        """
        #TODO Clean this up with new database
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

        """
        pass

    def check_host_name(self, task):
        host_name = socket.gethostname()
        if host_name == task["hostname"]:
            return True
        return False



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

