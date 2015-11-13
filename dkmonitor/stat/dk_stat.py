"""
This file contains the DkStat object that scans a given disk or directory
and stores the data in user and directory objects
"""


import shutil
import time
from pwd import getpwuid
import operator
import datetime
from collections import namedtuple

import sys, os
sys.path.append(os.path.abspath("../.."))

from dkmonitor.stat.dir_scan import dir_scan
#from dkmonitor.stat.user_obj import User
#from dkmonitor.stat.dir_obj import Directory
from dkmonitor.utilities import log_setup
from dkmonitor.config.settings_manager import export_settings

from dkmonitor.utilities.new_db_int import DataBase, UserStats, DirectoryStats

FileTuple = namedtuple('FileTuple', 'file_size last_access')
"""
class DkStat:
    This class is meant to gather stats on a disk or directory
    It stores stats in a directory object and separate user objects
    for each user

    def __init__(self, task):

        self.logger = log_setup.setup_logger(__name__)

        #Input search directory path verification exception
        try:
            os.listdir(task["target_path"])
        except OSError as err:
            self.logger.error("Directory path: %s is invalid", task["target_path"])
            raise err
        except PermissionError as err:
            self.logger.error("Invalid Permissions to: %s", task["target_path"])
            raise err


        self.task = task
        self.user_hash()
        self.settings = export_settings()
        self.database = DataBase(**self.settings["DataBase_Settings"])


    def dir_search(self):

        search_time = datetime.datetime.now()
        directory_obj = DirectoryStats(target_path=task["target_path"],
                                       hostname=task["hostname"],
                                       datetime=datetime.datetime.now()) #Creates dir_obj
        for file_path in dir_scan(task["target_path"]):
            last_access = (time.time() - os.path.getatime(file_path)) / 86400
            file_size = int(os.path.getsize(file_path))
            name = getpwuid(os.stat(file_path).st_uid).pw_name

            file_tup = FileTuple(file_size, last_access)
            directory_obj.add_file(file_tup, self.task["old_file_threshold"]) #Add file to directory obj

            try:
                self.user_hash[name].add_file(file_tup, self.task["old_file_threshold"])
            except KeyError:
                self.user_hash[name] = UserStats(username=name,
                                                 target_path=self.task["target_path"],
                                                 hostname=self.task["hostname"],
                                                 datetime=datetime.datetime.now())
                self.user_hash[name].add_file(file_tup, self.task["old_file_threshold"])

        rows = [x[1].calculate_stats() for x in self.user_hash.items()]
        rows.append(directory_obj.calculate_stats())
        self.database.store_rows(rows)


    def email_users(self, postfix, task_dict, current_use):

        problem_lists = self.get_problem_users(task_dict["Email_Settings"]["bad_flag_percent"])
        for user in self.user_hash.keys():
            self.user_hash[user].email_user(postfix, problem_lists, task_dict, current_use)


    def get_disk_use_percent(self):

        use = shutil.disk_usage(self.search_directory)
        use_percentage = use.used / use.total
        return use_percentage * 100


    def get_problem_users(self, problem_threshold):
        Returns a list of lists
        List in item one is the largest users of space
        List two is the largest holders of old data

        stat_list = []
        problem_threshold = problem_threshold / 100
        flag_user_number = int(len(self.user_hash.keys()) * problem_threshold)
        for user in self.user_hash.keys():
            stats = self.user_hash[user].get_stats()
            try:
                bpad = stats["total_file_size"]/stats["last_access_average"] #Bytes per access day
            except ZeroDivisionError:
                bpad = 0
            stat_list.append([user, stats["total_file_size"], bpad])

        large_list = sorted(stat_list, key=operator.itemgetter(1), reverse=True)[:flag_user_number]
        old_list = sorted(stat_list, key=operator.itemgetter(2), reverse=True)[:flag_user_number]

        large_names = []
        old_names = []
        for i in range(flag_user_number):
            large_names.append(large_list[i][0])
            old_names.append(old_list[i][0])

        return [large_names, old_names] #TODO change to a named tuple
    """

class DkStat:
    def __init__(self, task):
        self.task = task
        self.users = {}
        self.directory = None
        self.settings = export_settings()

    def scan(self):
        """Searches through the target_path for old files"""

        self.users = {}
        settings = export_settings()

        self.directory = DirectoryStats(target_path=self.task["target_path"],
                                       hostname=self.task["hostname"],
                                       datetime=datetime.datetime.now()) #Creates dir_obj
        for file_path in dir_scan(self.task["target_path"]):
            last_access = (time.time() - os.path.getatime(file_path)) / 86400
            file_size = int(os.path.getsize(file_path))
            name = getpwuid(os.stat(file_path).st_uid).pw_name

            file_tup = FileTuple(file_size, last_access)
            self.directory.add_file(file_tup, self.task["old_file_threshold"]) #Add file to directory obj

            try:
                self.users[name].add_file(file_tup, self.task["old_file_threshold"])
            except KeyError:
                self.users[name] = UserStats(username=name,
                                             target_path=self.task["target_path"],
                                             hostname=self.task["hostname"],
                                             datetime=datetime.datetime.now())
                users[name].add_file(file_tup, self.task["old_file_threshold"])

        for user in self.users.items():
            user.calculate_stats()
        self.directory.calculate_stats()

    def store(self):
        database = DataBase(**self.settings["DataBase_Settings"])

        rows = [x[1] for x in self.users.items()]
        rows.append(self.directory)
        database.store_rows(rows)

    def email(self):
        disk_use = self.get_disk_use_percent()
        problem_lists = self.get_problem_users()
        for user in self.users.items():
            user[1].email_user(self.settings["Email_Settings"]["user_postfix"], problem_lists, self.task, disk_use)

        problem_users = self.get_problem_users()

    def get_disk_use_percent(self):
        """Returns the disk use percentage of searched_directory"""

        use = shutil.disk_usage(self.task["target_path"])
        use_percentage = use.used / use.total
        return use_percentage * 100

    def get_problem_users(self):
        """
        Returns a list of lists
        List in item one is the largest users of space
        List two is the largest holders of old data
        """

        stat_list = []
        problem_threshold = self.task["email_top_percent"] / 100
        flag_user_number = int(len(users.keys()) * problem_threshold)
        for user in self.users.keys():
            try:
                bytes_per_access_time = user.stats["total_file_size"]/user.stats["total_access_time"] #Bytes per total access time 
            except ZeroDivisionError:
                bytes_per_access_time = 0
            stat_list.append([user, user.stats["total_file_size"], bytes_per_access_time])

        large_list = sorted(stat_list, key=operator.itemgetter(1), reverse=True)[:flag_user_number]
        old_list = sorted(stat_list, key=operator.itemgetter(2), reverse=True)[:flag_user_number]

        large_names = []
        old_names = []
        for i in range(flag_user_number):
            large_names.append(large_list[i][0])
            old_names.append(old_list[i][0])

        return [large_names, old_names] #TODO change to a named tuple


def scan_store_email(task):
    statobj = DkStat(task):

if __name__ == "__main__":
    pass



