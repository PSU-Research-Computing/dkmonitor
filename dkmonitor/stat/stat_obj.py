"""
stat_obj contains the abstract base class for dir_obj.py and user_obj.py
"""

import os
from collections import namedtuple

FileTuple = namedtuple('FileTuple', 'file_path file_size last_access')

class StatObj():
    """
    StatObj is an abstract base class for both dir_obj and user_obj.
    StatObj stores file data in a list
    It processes the file data internally and then can store
    it in a database or email a user if they are flagged
    """

    def __init__(self, tname, search_dir=None, system=None, datetime=None):

        self.table_name = tname

        self.collumn_dict = {'datetime': datetime,
                             'searched_directory': search_dir,
                             'system': system,
                             'total_file_size': None,
                             'disk_use_percent': None,
                             'last_access_average': None,
                             'disk_use_change': None,
                             'access_average_change': None}

        self.stat_dict = {'total_file_size': 0,
                          'number_of_files': 0,
                          'number_of_old_files' : 0,
                          'total_old_file_size' : 0,
                          'total_access_time': 0}


    def add_file(self, file_to_add, last_access_threshold):
        self.stat_dict["total_file_size"] += file_to_add.file_size
        self.stat_dict["number_of_files"] += 1
        self.stat_dict["total_access_time"] += file_to_add.last_access
        if file_to_add.last_access > last_access_threshold:
            self.stat_dict["number_of_old_files"] += 1
            self.stat_dict["total_old_file_size"] += file_to_add.file_size


    def export_data(self, db_obj):
        """Calculates stats and exports them to a database"""

        self.calculate_stats()
        self.get_set_query_data(db_obj.query_date_compare)
        self.insert_db_row(db_obj.store_row)

    def insert_db_row(self, db_insertion_function):
        """Inserts row of stats into a database"""

        column_list = []
        value_list = []

        for column in self.collumn_dict.keys():
            column_list.append(column)
            if (isinstance(self.collumn_dict[column], float) or
                    isinstance(self.collumn_dict[column], int)):
                value_list.append(str(self.collumn_dict[column]))
            elif (self.collumn_dict[column] == None):
                value_list.append("0")
            else:
                value_list.append("'" + str(self.collumn_dict[column]) + "'")

        ", ".join(column_list)
        ", ".join(value_list)

        db_insertion_function(self.table_name, [", ".join(column_list), ", ".join(value_list)])

    def build_query_str(self):
        """
        Builds a query string to get data from previous entry
        This function must be impleneted in the derived class
        """

        raise NotImplementedError()

    def get_set_query_data(self, db_query_function):
        """
        Gets data from previous entry
        Calculates new stats with prievious data
        Adds new stats to the objects dictionary
        """

        query_str = self.build_query_str()
        compare_str = "disk_use_percent, last_access_average"

        query_data = db_query_function(self.table_name, query_str, compare_str)

        #Checks for exsisting entries
        if query_data != None:
            query_data = query_data[0]
            disk_change = 0.0
            access_change = 0.0

            if self.collumn_dict["disk_use_percent"] == query_data[0]:
                disk_change = 0
            elif self.collumn_dict["disk_use_percent"] == 0:
                disk_change = -100.0
            elif query_data[0] == 0:
                disk_change = 100.0
            else:
                disk_change = self.collumn_dict["disk_use_percent"]/query_data[0]

            if self.collumn_dict["last_access_average"] == query_data[1]:
                access_change = 0
            elif self.collumn_dict["last_access_average"] == 0:
                access_change = -100.0
            elif query_data[1] == 0:
                access_change = 100.0
            else:
                access_change = self.collumn_dict["last_access_average"]/query_data[1]

            self.collumn_dict["disk_use_change"] = disk_change
            self.collumn_dict["access_average_change"] = access_change

    def get_stats(self):
        """Returns specific stats"""

        self.calculate_stats()
        return {"total_file_size": self.collumn_dict["total_file_size"],
                "last_access_average": self.collumn_dict["last_access_average"]}

#####DATA PROCESSING FUCNTIONS##################
    def get_total_space(self):
        """Calculates total file size of all files in file_list"""

        self.collumn_dict["total_file_size"] = self.stat_dict["total_file_size"]

    def get_disk_use_percentage(self):
        """Calculates the disk use percentage of all files"""

        if self.collumn_dict["total_file_size"] is None:
            self.get_total_space()

        stat_tup = os.statvfs(self.collumn_dict["searched_directory"]) #TODO try except
        total = stat_tup.f_blocks * stat_tup.f_frsize

        user_percentage = 100 * float(self.collumn_dict["total_file_size"])/float(total)
        self.collumn_dict["disk_use_percent"] = user_percentage


    def get_access_average(self):
        """Calculates the last access average for all stored files"""

        try: #possibly change this to an if statement
            average_last_access = self.stat_dict["total_access_time"] / self.stat_dict["number_of_old_files"]
        except ZeroDivisionError:
            average_last_access = self.stat_dict["total_access_time"]

        self.collumn_dict["last_access_average"] = average_last_access

    def calculate_stats(self):
        """Caclutes all stats"""

        self.get_total_space()
        self.get_disk_use_percentage()
        self.get_access_average()

