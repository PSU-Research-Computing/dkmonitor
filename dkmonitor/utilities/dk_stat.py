"""
This file contains the DkStat object that scans a given disk or directory
and stores the data in user and directory objects
"""

import shutil, time, operator, datetime, pwd
from collections import namedtuple

import sys, os
sys.path.append(os.path.abspath("../.."))

from dkmonitor.utilities.dir_scan import dir_scan
from dkmonitor.utilities import log_setup
from dkmonitor.config.settings_manager import export_settings
from dkmonitor.database_manager import DataBase, UserStats, DirectoryStats
from dkmonitor.config.task_manager import check_alteration_settings, check_relocate

FileTuple = namedtuple('FileTuple', 'file_size last_access')

class DkStat:
    """
    DkStat is a class used to build user and system statictics
    as well as nofitications
    """

    def __init__(self, task):
        self.task = task
        self.users = {}
        self.directory = None
        self.settings = export_settings()
        self.logger = log_setup.setup_logger(__name__)

    def scan(self):
        """Searches through the target_path for old files"""
        print("Scanning...")
        self.logger.info("Scanning %s on %s", self.task["target_path"], self.task["hostname"])

        self.users = {}

        self.directory = DirectoryStats(target_path=self.task["target_path"],
                                        hostname=self.task["hostname"],
                                        taskname=self.task["taskname"],
                                        datetime=datetime.datetime.now())
        self.directory.disk_use_percent = get_disk_use_percent(self.task["target_path"])

        for file_path in dir_scan(self.task["target_path"]):
            last_access = (time.time() - os.path.getatime(file_path)) / 86400
            file_size = int(os.path.getsize(file_path))
            name = pwd.getpwuid(os.stat(file_path).st_uid).pw_name

            file_tup = FileTuple(file_size, last_access)
            self.directory.add_file(file_tup, self.task["old_file_threshold"])

            try:
                self.users[name].add_file(file_tup, self.task["old_file_threshold"])
            except KeyError:
                self.users[name] = UserStats(username=name,
                                             target_path=self.task["target_path"],
                                             hostname=self.task["hostname"],
                                             taskname=self.task["taskname"],
                                             datetime=datetime.datetime.now())
                self.users[name].add_file(file_tup, self.task["old_file_threshold"])

        for _, user in self.users.items():
            user.calculate_stats()
        self.directory.calculate_stats()

    def store(self):
        """Stores all stats in the database"""
        print("Storing stats")
        self.logger.info("Storing stats from %s on %s",
                         self.task["target_path"],
                         self.task["hostname"])

        database = DataBase(**self.settings["DataBase_Settings"])

        rows = [x[1] for x in self.users.items()]
        rows.append(self.directory)
        database.store(rows)

    def email_users(self):
        """Emails users if nessesary"""
        disk_use = get_disk_use_percent(self.task["target_path"])
        if (check_alteration_settings(self.task) is True) and \
           (self.task["email_data_alterations"] is True) and \
           (disk_use > self.task["usage_critical_threshold"]):

            print("Emailing Data alteration notices")
            for _, user in self.users.items():
                if check_relocate(self.task) is True:
                    user.email_alteration_notice(self.task,
                                                 self.settings["Email_Settings"]["user_postfix"],
                                                 "file_move_notice")
                elif self.task["delete_old_files"] is True:
                    user.email_alteration_notice(self.task,
                                                 self.settings["Email_Settings"]["user_postfix"],
                                                 "file_deletion_notice")

        elif (disk_use > self.task["usage_warning_threshold"]) and \
             (self.task["email_usage_warnings"] is True):
            print("Emailing Usage Warnings")
            problem_users = self.get_problem_users()
            for _, user in self.users.items():
                user.email_usage_warning(self.task,
                                         self.settings["Email_Settings"]["user_postfix"],
                                         problem_users)
            self.logger.info("Emailing users on %s", self.task["hostname"])




    def get_problem_users(self):
        """
        Returns a list of lists
        List in item one is the largest users of space
        List two is the largest holders of old data
        """
        stat_list = []
        try:
            problem_threshold = self.task["email_top_percent"] / 100
        except TypeError:
            problem_threshold = .25 #Set default to 25% if email_top_percent not specifed

        flag_user_number = int(len(self.users.keys()) * problem_threshold)
        for username, user in self.users.items():
            try:
                bytes_per_access_time = user.total_file_size_count/\
                                        user.total_access_time_count #Bytes per total access time
            except ZeroDivisionError:
                bytes_per_access_time = 0
            stat_list.append([username, user.total_file_size_count, bytes_per_access_time])

        large_list = sorted(stat_list, key=operator.itemgetter(1), reverse=True)[:flag_user_number]
        old_list = sorted(stat_list, key=operator.itemgetter(2), reverse=True)[:flag_user_number]

        large_names = []
        old_names = []
        for i in range(flag_user_number):
            large_names.append(large_list[i][0])
            old_names.append(old_list[i][0])

        return [large_names, old_names]

    def display_stats(self):
        """Displays all stats collected durring the scan"""
        self.directory.display_stats()
        sorted_user_keys = sorted(self.users,
                                  key=lambda user: self.users[user].total_file_size_count,
                                  reverse=True)
        for user in sorted_user_keys:
            self.users[user].display_stats()

def scan_store_email(task):
    """Function that runs entire scan routine on a task"""
    statobj = DkStat(task)
    statobj.scan()
    statobj.store()
    statobj.email_users()

def scan_store_email_display(task):
    """Function that runs entire scan routine and displays the stats"""
    statobj = DkStat(task)
    statobj.scan()
    statobj.store()
    statobj.email_users()
    statobj.display_stats()

def get_disk_use_percent(path):
    """Returns the disk use percentage of searched_directory"""
    use = shutil.disk_usage(path)
    use_percentage = use.used / use.total
    return use_percentage * 100
