import os
from collections import namedtuple
#from dk_stat import User_file

User_file = namedtuple('User_file', 'file_path file_size last_access')

class User():
    def __init__(self, name, search_dir=None, datetime=None, total_file_size=None, use_percent=None, use_percent_change=0.0, average_access=None, avrg_access_change=0.0):

        self.collumn_dict = {
            'user_name': name,
            'datetime': datetime,
            'searched_directory': search_dir,
            'total_file_size': total_file_size,
            'disk_use_percent': use_percent,
            'last_access_average': average_access,
            'disk_use_change': use_percent_change,
            'access_average_change': avrg_access_change
        }

        self.file_list = []

    def add_file(self, file_to_add):
        self.file_list.append(file_to_add)

    def get_total_user_space(self):
        total_space = 0
        for user_file in self.file_list:
            total_space += int(user_file.file_size)

        self.collumn_dict["total_file_size"] = total_space


    def get_disk_use_percentage(self):
        if self.collumn_dict["total_file_size"] == None:
            self.get_total_user_space()

        st = os.statvfs(self.collumn_dict["searched_directory"]) #TODO try except
        total = st.f_blocks * st.f_frsize

        user_percentage = 100 * float(self.collumn_dict["total_file_size"])/float(total)
        self.collumn_dict["use_percent"] = user_percentage


    def get_user_access_average(self):
        total_time = 0
        file_count = 0
        for user_file in self.file_list:
            total_time += user_file.last_access
            file_count += 1


        try: #possibly change this to an if statement
            average_last_access = total_time / file_count
        except ZeroDivisionError:
            average_last_access = total_time

        self.collumn_dict["access_average_change"] = average_last_access


    def get_old_file_list(self, minimum_day_num):
        flaged_files = []
        for user_file in self.file_list:
            if user_file.last_access > minimum_day_num:
                flaged_files.append(user_file.file_path)

        return flaged_files

    def calculate_stats(self):
        self.get_total_user_space()
        self.get_disk_use_percentage()
        self.get_user_access_average()

    #TODO test this function
    def get_set_query_data(self, db_query_function):
        query_str = "user_name = '{name}' AND searched_directory = '{sdir}'".format(name=self.collumn_dict["user_name"],
                sdir=self.collumn_dict["searched_directory"])
        compare_str = "disk_use_percent, last_access_average"

        print ("querying Data... ")
        query_data = db_query_function("user_stats", query_str, compare_str)

        print (query_data)
        if query_data != None:
            self.collumn_dict["disk_use_change"] = query_data[1]
            self.collumn_dict["access_average_change"] = query_data[0]


    def insert_db_row(self, db_insertion_function):
        table_name = "user_stats"
        column_list = []
        value_list = []
        column_str = ""
        value_str = ""

        for column in self.collumn_dict.keys():
            column_list.append(column)
            if type(self.collumn_dict[column]) is float or type(self.collumn_dict[column]) is int:
                value_list.append(str(self.collumn_dict[column]))
            else:
                value_list.append("'" + str(self.collumn_dict[column]) + "'")

            column_str += column + ", "
            value_str += "'" + str(self.collumn_dict[column]) + "'" + ", "

        ", ".join(column_list)
        ", ".join(value_list)

        db_insertion_function(table_name, [", ".join(column_list), ", ".join(value_list)])

    def export_user(self, db_obj):
        self.get_set_query_data(db_obj.query_date_compare)
        self.insert_db_row(db_obj.store_row)

    def export_data(self):
        self.calculate_stats()
        join_list = [self.collumn_dict["user_name"], str(self.collumn_dict["datetime"]), self.collumn_dict["searched_directory"], str(self.collumn_dict["total_file_size"]), str(self.collumn_dict["disk_use_percent"]), str(self.collumn_dict["last_access_average"])]
        return " ".join(join_list)








