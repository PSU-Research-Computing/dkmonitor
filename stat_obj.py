import os
from collections import namedtuple
from io import StringIO
import json

file_tuple = namedtuple('file_tuple', 'file_path file_size last_access')
stat_tuple = namedtuple('stat_tuple', 'total_file_size last_access_average')

class Stat_obj():
    def __init__(self,
                 tname,
                 search_dir=None,
                 system=None,
                 datetime=None,
                 total_file_size=None,
                 use_percent=None,
                 use_percent_change=0.0,
                 average_access=None,
                 avrg_access_change=0.0):

        self.file_list = []
        self.table_name = tname

        self.collumn_dict = {'datetime': datetime,
                             'searched_directory': search_dir,
                             'system': system,
                             'total_file_size': total_file_size,
                             'disk_use_percent': use_percent,
                             'last_access_average': average_access,
                             'disk_use_change': use_percent_change,
                             'access_average_change': avrg_access_change}

    #Adds file to the list of associated files
    def add_file(self, file_to_add):
        self.file_list.append(file_to_add)

    #Calculates stats and exports them to a database
    def export_data(self, db_obj):
        self.calculate_stats()
        self.get_set_query_data(db_obj.query_date_compare)
        self.insert_db_row(db_obj.store_row)

    #Inserts row of stats into a database
    def insert_db_row(self, db_insertion_function):
        column_list = []
        value_list = []

        for column in self.collumn_dict.keys():
            column_list.append(column)
            if type(self.collumn_dict[column]) is float or type(self.collumn_dict[column]) is int:
                value_list.append(str(self.collumn_dict[column]))
            else:
                value_list.append("'" + str(self.collumn_dict[column]) + "'")

        ", ".join(column_list)
        ", ".join(value_list)

        db_insertion_function(self.table_name, [", ".join(column_list), ", ".join(value_list)])

    #Builds a query string to get data from previous entry
    def build_query_str(self): #This function must be impleneted in the derived class
        raise NotImplementedError()

    #gets data from previous entry
    #Calculates new stats with prievious data
    #Adds new stats to the objects dictionary
    def get_set_query_data(self, db_query_function):
        query_str = self.build_query_str()
        compare_str = "disk_use_percent, last_access_average"

        query_data = db_query_function(self.table_name, query_str, compare_str)

        #Checks for exsisting entries
        if query_data != None:
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

    #Returns specific stats 
    def get_stats(self):
        self.calculate_stats()
        #return_stat = stat_tuple(self.collumn_dict["total_file_size"], self.collumn_dict["last_access_average"])
        return [self.collumn_dict["total_file_size"], self.collumn_dict["last_access_average"]]

#####DATA PROCESSING FUCNTIONS##################
    def get_total_space(self):
        total_space = 0
        for file_tuple in self.file_list:
            total_space += int(file_tuple.file_size)

        self.collumn_dict["total_file_size"] = total_space

    def get_disk_use_percentage(self):
        if self.collumn_dict["total_file_size"] == None:
            self.get_total_space()

        st = os.statvfs(self.collumn_dict["searched_directory"]) #TODO try except
        total = st.f_blocks * st.f_frsize

        user_percentage = 100 * float(self.collumn_dict["total_file_size"])/float(total)
        self.collumn_dict["disk_use_percent"] = user_percentage


    def get_access_average(self):
        total_time = 0
        file_count = 0
        for file_tuple in self.file_list:
            total_time += file_tuple.last_access
            file_count += 1

        try: #possibly change this to an if statement
            average_last_access = total_time / file_count
        except ZeroDivisionError:
            average_last_access = total_time

        self.collumn_dict["last_access_average"] = average_last_access


    def build_old_file_attachment(self, minimum_day_num):
        attachment = StringIO()
        for file_tup in self.file_list:
            if file_tup.last_access > minimum_day_num:
                attachment.write(file_tup.file_path + '\n')

        return attachment

    def build_json_stream(self, access_day_threshold, file_size_threshold, percentage_threshold):
        attachment = StringIO()
        tmp_dict = {'user_name': self.collumn_dict["user_name"],
                    'system': self.collumn_dict['system'],
                    'directory': self.collumn_dict['searched_directory'],
                    'access_day_threshold': access_day_threshold,
                    'file_size_threshold': file_size_threshold,
                    'percentage_threshold': percentage_threshold}
        json.dump(tmp_dict, attachment)
        return attachment


    def calculate_stats(self):
        self.get_total_space()
        self.get_disk_use_percentage()
        self.get_access_average()

