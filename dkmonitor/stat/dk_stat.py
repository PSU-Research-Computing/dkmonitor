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
from dkmonitor.stat.user_obj import User
from dkmonitor.stat.dir_obj import Directory
from dkmonitor.utilities import log_setup

FileTuple = namedtuple('FileTuple', 'file_size last_access')

class DkStat:
    """
    This class is meant to gather stats on a disk or directory
    It stores stats in a directory object and separate user objects
    for each user
    """

    def __init__(self, system=None, search_dir=None):

        self.logger = log_setup.setup_logger("dk_stat_log.log")

        #Input search directory path verification exception
        try:
            os.listdir(search_dir)
        except:
            self.logger.error("Directory path: %s is invalid", search_dir)
            raise Exception("Directory path: {dir} is invalid.".format(dir=search_dir))

        self.user_hash = {}
        self.directory_obj = None
        self.system = system
        self.search_directory = search_dir


    def dir_search(self, last_access_threshold):
        search_time = datetime.datetime.now()
        self.directory_obj = Directory(search_dir=self.search_directory,
                                       system=self.system,
                                       datetime=search_time) #Creates dir_obj
        for file_path in dir_scan(self.search_directory):
            last_access = (time.time() - os.path.getatime(file_path)) / 86400
            file_size = int(os.path.getsize(file_path))
            name = getpwuid(os.stat(file_path).st_uid).pw_name

            file_tup = FileTuple(file_size, last_access)
            self.directory_obj.add_file(file_tup, last_access_threshold) #Add file to directory obj

            try:
                self.user_hash[name].add_file(file_tup, last_access_threshold)
            except KeyError:
                self.user_hash[name] = User(name,
                                            search_dir=self.search_directory,
                                            system=self.system,
                                            datetime=search_time)
                self.user_hash[name].add_file(file_tup, last_access_threshold)

    def export_data(self, db_obj):
        """Exports the file data from the User dict to a database object"""

        self.directory_obj.export_data(db_obj)
        for user in self.user_hash.keys():
            self.user_hash[user].export_data(db_obj)

    def email_users(self, postfix, task_dict, current_use):
        """Flaggs users, and then sends out email warnings"""

        problem_lists = self.get_problem_users(task_dict["bad_flag_percent"])
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

        print("Total users: {flag}".format(flag=len(self.user_hash.keys())))
        print("Total Flagged users: {flag}".format(flag=flag_user_number))
        large_list = sorted(stat_list, key=operator.itemgetter(1), reverse=True)[:flag_user_number]
        print(large_list)
        old_list = sorted(stat_list, key=operator.itemgetter(2), reverse=True)[:flag_user_number]

        large_names = []
        old_names = []
        for i in range(flag_user_number):
            large_names.append(large_list[i][0])
            old_names.append(old_list[i][0])

        return [large_names, old_names] #TODO change to a named tuple

####JUNK FUNCTIONS#########################
    def dir_scan(self, stat_function=None, recursive_dir=None): #possibly divide into multiple fucntions
        """
        Searches through entire directory tree recursively
        Saves file info in a dict sorted by user
        """

        if recursive_dir == None:
            self.search_time = datetime.datetime.now()
            self.directory_obj = Directory(search_dir=self.search_directory,
                                           system=self.system,
                                           datetime=self.search_time) #Creates dir_obj

            self.dir_scan(stat_function=stat_function, recursive_dir=self.search_directory) #starts recursive call

        else:
            if os.path.isdir(recursive_dir):
                content_list = os.listdir(recursive_dir)
                for i in content_list:
                    current_path = recursive_dir + '/' + i
                    if os.path.isfile(current_path): #If dir is a file, check when it was modified
                        if stat_function is None:
                            self.logger.warning("Function passed into dir_scan is None type")
                        else:
                            stat_function(current_path)

                    else:
                        try:
                            #recursive call on every directory
                            self.dir_scan(stat_function=stat_function, recursive_dir=(current_path))
                        except OSError as oerror:
                            self.logger.info(oerror)

    def build_file_info(self, file_path):
        last_access = (time.time() - os.path.getatime(file_path)) / 86400
        file_size = int(os.path.getsize(file_path))
        name = getpwuid(os.stat(file_path).st_uid).pw_name

        file_tup = FileTuple(file_path, file_size, last_access)
        self.directory_obj.add_file(file_tup) #Add file to directory obj

        #if name has not already be found then add to user_hash
        try:
            self.user_hash[name].add_file(file_tup)
        except KeyError:
            self.user_hash[name] = User(name,
                                        search_dir=self.search_directory,
                                        system=self.system,
                                        datetime=self.search_time)
            self.user_hash[name].add_file(file_tup)

if __name__ == "__main__":
    pass



