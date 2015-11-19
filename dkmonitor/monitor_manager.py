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

class ScanTypeNotFound(Exception):
    def __init__(self, message):
        super(ScanTypeNotFound, self).__init__(message)

class MonitorManager():
    """This class is the main managing class for all other classes
    It runs preset tasks that are found in a database"""

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
        saves disk statistics information in db
        if over quota, email users / clean disk if neccessary
        """
        print("Starting Full Scan of: {}".format(task["target_path"]))

        scan_store_email(task)
        self.check_then_clean(task)


    def check_then_clean(self, task):
        """Cleaning routine function"""

        if (task["relocation_path"] is not None) or (task["delete_old_files"] is True):
            print("Checking if disk: '{}' needs to be cleaned".format(task["target_path"]))

            disk_use = get_disk_use_percent(task["target_path"])
            if disk_use > task["usage_critical_threshold"]:

                thread_settings = self.settings["Thread_Settings"]
                clean_obj = DkClean(task)

                if task["relocation_path"] is not None:
                    print("Relocating Files")
                    if thread_settings["thread_mode"] == "yes":
                        clean_obj.move_all_threaded(thread_settings["thread_number"], delete_if_full=task["delete_when_full"])
                    else:
                        clean_obj.move_all(delete_when_full=task["delete_when_full"])

                elif task["delete_old_files"] is True:
                    print("Deleting Old Files")
                    if thread_settings["thread_mode"] == "yes":
                        clean_obj.delete_all_threaded(thread_settings["thread_number"])
                    else:
                        clean_obj.delete_all()
            else:
                print("Disk: '{}' does not need to be cleaned".format(task["target_path"]))


    def start_scans(self, scan_type="full"):
        """ """
        if scan_type == "full":
            scan_function = self.full_scan
        elif scan_type == "quick":
            scan_function = self.quick_scan
        else:
            raise ScanTypeNotFound("Scan type '{}' was not found".format(scan_type))

        for key, task in list(self.tasks.items()):
            if check_host_name(task) is True:
                if self.settings["Thread_Settings"]["thread_mode"] == "yes":
                    thread = threading.Thread(target=self.scan_wrapper, args=(scan_function,task,))
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
    parser.add_argument("scan_type", help="Specify scan type: 'quick' or 'full'")
    args = parser.parse_args()
    monitor.start_scans(args.scan_type)


if __name__ == "__main__":
    main()

