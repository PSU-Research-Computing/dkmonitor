"""
This script Is the main managing script for the dk_monitor script suite.
This script is indented to be run as a cron job to monitor actions on any
given disk or directory that is set by the adminstrator
"""

import threading, argparse, socket

import sys, os
sys.path.append(os.path.abspath(".."))

from dkmonitor.utilities import log_setup
from dkmonitor.config.settings_manager import export_settings
from dkmonitor.config.task_manager import export_tasks

from dkmonitor.utilities.database_manager import clean_database
from dkmonitor.utilities.dk_clean import check_then_clean
from dkmonitor.stat.dk_stat import scan_store_email, get_disk_use_percent

class ScanTypeNotFound(Exception):
    """Error thrown when scan type is invalid"""
    def __init__(self, message):
        super(ScanTypeNotFound, self).__init__(message)

class IncorrectHostError(Exception):
    """Error thrown when task doesnt match current hostname"""
    def __init__(self, message):
        super(IncorrectHostError, self).__init__(message)

class MonitorManager():
    """
    This class is the main managing class for all classes that scan, clean and email
    It runs preset tasks that are found in a database
    """

    def __init__(self):
        self.settings = export_settings()
        self.tasks = export_tasks()

        self.logger = log_setup.setup_logger(__name__)

        if self.settings["DataBase_Cleaning_Settings"]["purge_database"] == "yes":
            self.logger.info("Cleaning Database")
            clean_database(self.settings["DataBase_Cleaning_Settings"]["purge_after_day_number"])

    def scan_wrapper(self, scan, task):
        """Error catching wrapper for quick and full scan fucntions"""
        try:
            print("Running Task: '{}'".format(task["taskname"]))
            scan(task)
            print("Task: '{}' is complete".format(task["taskname"]))
            self.logger.info("Task: %s complete!", task["taskname"])
        except PermissionError:
            print("You do not have permissions to {}".format(task["target_path"]), file=sys.stderr)
        except OSError:
            print("There is no directory: {}".format(task["target_path"]), file=sys.stderr)

    @staticmethod
    def quick_scan(task):
        """
        Meant to be run hourly
        Checks use percent on a task
        if over quota, email users / clean disk if neccessary
        """
        print("Starting Quick Scan of: {}".format(task["target_path"]))

        disk_use = get_disk_use_percent(task["target_path"])
        if disk_use > task["usage_warning_threshold"]:
            print("Disk use over threshold, Starting full scan of {}".format(task["target_path"]))
            scan_store_email(task)
            check_then_clean(task)

    @staticmethod
    def full_scan(task):
        """
        Performs full scan of directory by default
        saves disk statistics information in db
        if over quota, email users / clean disk if neccessary
        """
        print("Starting Full Scan of: {}".format(task["target_path"]))

        scan_store_email(task)
        check_then_clean(task)

    def run_task(self, task, scan_function):
        """Runs a single task"""
        check_host_name(task) #raises error if does not match
        if task["enabled"] is True:
            if self.settings["Thread_Settings"]["thread_mode"] == "yes":
                thread = threading.Thread(target=self.scan_wrapper, args=(scan_function, task,))
                thread.daemon = False
                thread.start()
            else:
                self.scan_wrapper(scan_function, task)

    def start_tasks(self, scan_type="full"):
        """Starts all tasks that are on current host"""
        try:
            scan_function = self.get_scan_function(scan_type)
            scan_started_flag = False
            for task in list(self.tasks.items()):
                try:
                    self.run_task(task[1], scan_function)
                    scan_started_flag = True
                except IncorrectHostError:
                    pass

            if scan_started_flag is False:
                print("No tasks to preform")
        except ScanTypeNotFound:
            print("Scan type '{}' is invalid, specify either 'quick' or 'full'".format(scan_type),
                  file=sys.stderr)

    def start_task(self, task_name, scan_type='full'):
        """Starts a task givin by the user"""
        try:
            task = self.tasks[task_name]
            scan_function = self.get_scan_function(scan_type)
            self.run_task(task, scan_function)
        except KeyError:
            print("Task '{}' not found".format(task_name), file=sys.stderr)
        except ScanTypeNotFound:
            print("Scan type '{}' is invalid, specify either 'quick' or 'full'".format(scan_type),
                  file=sys.stderr)
        except IncorrectHostError:
            print("Task '{}' hostname does not match current host".format(task["hostname"]),
                  file=sys.stderr)

    def get_scan_function(self, scan_type):
        """
        Checks if string is 'full' or 'quick' and returns the corrisponding function
        Raises error if string is neither
        """
        if scan_type == "full":
            scan_function = self.full_scan
        elif scan_type == "quick":
            scan_function = self.quick_scan
        else:
            raise ScanTypeNotFound("Scan type '{}' was not found".format(scan_type))
        return scan_function

def check_host_name(task):
    """
    Gets current hostname and compares with a task
    Raises error if hostname does not match
    """
    host_name = socket.gethostname()
    if host_name != task["hostname"]:
        raise IncorrectHostError("Hostname '{th}' does not match '{ch}'".format(th=task["hostname"],
                                                                                ch=host_name))

def main(args=None):
    """Monitor Manager Command line interface"""
    if args is None:
        args = sys.argv[1:0]

    description = "The run command line interface is used to run tasks on the current machine"
    parser = argparse.ArgumentParser(description=description)
    subparsers = parser.add_subparsers()
    all_parser = subparsers.add_parser("all")
    all_parser.set_defaults(which="all")
    all_parser.add_argument("scan_type", help="Specify scan type: 'quick' or 'full'")

    task_parser = subparsers.add_parser("task")
    task_parser.set_defaults(which="task")
    task_parser.add_argument("task_name", help="Name of task to run")
    task_parser.add_argument("scan_type", help="Specify scan type: 'quick' or 'full'")

    args = parser.parse_args(args)
    monitor = MonitorManager()
    if args.which == "all":
        monitor.start_tasks(scan_type=args.scan_type)
    elif args.which == "task":
        monitor.start_task(args.task_name, scan_type=args.scan_type)

if __name__ == "__main__":
    main()

