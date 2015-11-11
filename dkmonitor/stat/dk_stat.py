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

class DkStat:
    """
    This class is meant to gather stats on a disk or directory
    It stores stats in a directory object and separate user objects
    for each user
    """

    def __init__(self, system=None, search_dir=None):

        self.logger = log_setup.setup_logger(__name__)

        #Input search directory path verification exception
        try:
            os.listdir(search_dir)
        except OSError as err:
            self.logger.error("Directory path: %s is invalid", search_dir)
            raise err
        except PermissionError as err:
            self.logger.error("Invalid Permissions to: %s", search_dir)
            raise err

        self.user_hash = {}
        self.directory_obj = None
        self.system = system
        self.search_directory = search_dir

        self.settings = export_settings()
        self.database = DataBase(**settings["DataBase_Settings"])


    def dir_search(self, last_access_threshold):
        """Searches through the self.search_directory for old files"""

        search_time = datetime.datetime.now()
        self.directory_obj = DirectoryStats(target_path=self.search_directory,
                                            hostname=self.system,
                                            datetime=datetime.datetime.now()) #Creates dir_obj
        for file_path in dir_scan(self.search_directory):
            last_access = (time.time() - os.path.getatime(file_path)) / 86400
            file_size = int(os.path.getsize(file_path))
            name = getpwuid(os.stat(file_path).st_uid).pw_name

            file_tup = FileTuple(file_size, last_access)
            self.directory_obj.add_file(file_tup, last_access_threshold) #Add file to directory obj

            try:
                self.user_hash[name].add_file(file_tup, last_access_threshold)
            except KeyError:
                self.user_hash[name] = UserStats(username=name,
                                                 target_path=self.search_directory,
                                                 hostname=self.system,
                                                 datetime=datetime.datetime.now())
                self.user_hash[name].add_file(file_tup, last_access_threshold)

        rows = [x[1].calculate_stats() for x in self.user_hash.items()]
        rows.append(self.directory_obj)
        database.store_rows(rows)

    def export_rows(self):
        rows = [x[1].calculate_stats() for x in self.user_hash.items()]
        rows.append(self.directory_obj)
        return rows

    def export_data(self, db_obj):
        """Exports the file data from the User dict to a database object"""

        self.directory_obj.export_data(db_obj)
        for user in self.user_hash.keys():
            self.user_hash[user].export_data(db_obj)

    def email_users(self, postfix, task_dict, current_use):
        """Flaggs users, and then sends out email warnings"""

        problem_lists = self.get_problem_users(task_dict["Email_Settings"]["bad_flag_percent"])
        for user in self.user_hash.keys():
            self.user_hash[user].email_user(postfix, problem_lists, task_dict, current_use)


    def get_disk_use_percent(self):
        """Returns the disk use percentage of searched_directory"""

        use = shutil.disk_usage(self.search_directory)
        use_percentage = use.used / use.total
        return use_percentage * 100


    def get_problem_users(self, problem_threshold):
        """
        Returns a list of lists
        List in item one is the largest users of space
        List two is the largest holders of old data
        """

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

if __name__ == "__main__":
    pass



