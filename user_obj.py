import os
from collections import namedtuple
#from dk_stat import User_file

User_file = namedtuple('User_file', 'file_path file_size last_access')

class User():
    def __init__(self, name, search_dir=None, datetime=None, total_file_size=None, use_percent=None, average_access=None):

        self.collumn_dict = {'user_name': name, 'datetime': datetime, 'searched_directory': search_dir, 'total_file_size': total_file_size,
                            'use_percent': use_percent, 'average_access': average_access, 'use_percent_change': None,
                            'access_change': None}
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

        self.collumn_dict["average_access"] = average_last_access


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
        query_str = "user_name = {name} AND searched_directory = {sdir}".format(name=self.collumn_dict["user_name"],
                sdir=self.collumn_dict["searched_directory"])
        compare_str = "disk_use_percent, last_access_average"

        query_data = db_query_function("user_stats", query_str, compare_str)

        self.collumn_dict["disk_use_change"] = query_data[1]
        self.collumn_dict["access_averaage_change"] = query_data[0]

    def export_data(self):
        self.calculate_stats()
        join_list = [self.collumn_dict["user_name"], str(self.collumn_dict["datetime"]), self.collumn_dict["searched_directory"], str(self.collumn_dict["total_file_size"]), str(self.collumn_dict["use_percent"]), str(self.collumn_dict["average_access"])]
        return " ".join(join_list)








