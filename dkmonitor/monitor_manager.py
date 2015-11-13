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

from dkmonitor.utilities.new_db_int import DataBase
from dkmonitor.utilities.dk_clean import DkClean
from dkmonitor.utilities import log_setup

from dkmonitor.config.settings_manager import export_settings
from dkmonitor.config.task_manager import export_tasks

from dkmonitor.stat.dk_stat import scan_store_email, get_disk_use_percent

class MonitorManager():
    """This class is the main managing class for all other classes
    It runs preset tasks that are found in the json settings file"""

    def __init__(self):
        self.settings = export_settings()
        self.tasks = export_tasks()

        self.logger = log_setup.setup_logger(__name__)

        if self.settings["DataBase_Cleaning_Settings"]["purge_database"] == "yes":
            self.logger.info("Cleaning Database")
            #self.database.clean_data_base(self.settings["DataBase_Cleaning_Settings"]["purge_after_day_number"])

    def scan_wrapper(self, scan, task):
        try:
            print("Running Task: '{}'".format(task["taskname"]))
            scan(task)
            print("Task: '{}' is complete".format(task["taskname"]))
            self.logger.info("Task: %s complete!", task["taskname"])
        except PermissionError:
            print("You do not have permissions to {}".format(task["target_path"]), file=sys.stderr)
        except OSError:
            print("There is no directory: {}".format(task["target_path"]), file=sys.stderr)

    def quick_scan(self, task):
        """
        Ment to be run hourly
        Checks use percent on a task
        if over quota, email users / clean disk if neccessary
        """
        print("Starting Quick Scan of: {}".format(task["target_path"]))

        disk_use = get_disk_use_percent(task["target_path"])
        if disk_use > task["usage_warning_threshold"]:
            scan_store_email(task)
            self.check_then_clean(task)

    def full_scan(self, task):
        """
        Performs full scan of directory by default
        logs disk statistics information in db
        if over quota, email users / clean disk if neccessary
        """
        print("Starting Full Scan of: {}".format(task["target_path"]))

        scan_store_email(task)
        self.check_then_clean(task)


    def check_then_clean(self, task):
        """Cleaning routine function"""

        if (task["relocation_path"] != "") or (task["delete_old_files"] is True):
            print("Checking if disk: '{}' needs to be cleaned".format(task["target_path"]))

            disk_use = get_disk_use_percent(task["target_path"])
            if disk_use > task["usage_critical_threshold"]:

                thread_settings = self.settings["Thread_Settings"]
                clean_obj = DkClean(task)

                if task["relocation_path"] != "":
                    print("Relocating Files")
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
                    print("Deleting Old Files")
                    if thread_settings["thread_mode"] == "yes":
                        clean_obj.delete_all_threaded(thread_settings["thread_number"])
                    else:
                        clean_obj.delete_all()
            else:
                print("Disk: '{}' does not need to be cleaned".format(task["target_path"]))


    #TODO Combine into one function
    def start_full_scans(self):
        """starts full scan on tasks"""

        print("Starting Full Scans")

        for key, task in list(self.tasks.items()):
            if check_host_name(task) is True:
                if self.settings["Thread_Settings"]["thread_mode"] == "yes":
                    thread = threading.Thread(target=self.scan_wrapper, args=(self.full_scan,task,))
                    thread.daemon = False
                    thread.start()
                else:
                    self.scan_wrapper(self.full_scan, task)


    def start_quick_scans(self):
        """Starts quick scan on tasks"""

        print("Starting Quick Scans")

        for key, task in list(self.tasks.items()):
            if check_host_name(task) is True:
                if self.settings["Thread_Settings"]["thread_mode"] == "yes":
                    thread = threading.Thread(target=self.scan_wrapper, args=(self.quick_scan,task,))
                    thread.daemon = False
                    thread.start()
                else:
                    self.scan_wrapper(self.quick_scan, task)


def check_host_name(task):
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

