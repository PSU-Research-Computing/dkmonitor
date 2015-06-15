import os
from collections import namedtuple

file_tuple = namedtuple('file_tuple', 'file_path file_size last_access')

class Stat_obj():
    def __init__(self,
            tname,
            search_dir=None,
            datetime=None,
            total_file_size=None,
            use_percent=None,
            use_percent_change=0.0,
            average_access=None,
            avrg_access_change=0.0
            ):

        self.file_list = []
        self.table_name = tname

        self.collumn_dict = {
            'datetime': datetime,
            'searched_directory': search_dir,
            'total_file_size': total_file_size,
            'disk_use_percent': use_percent,
            'last_access_average': average_access,
            'disk_use_change': use_percent_change,
            'access_average_change': avrg_access_change
        }

    def add_file(self, file_to_add):
        self.file_list.append(file_to_add)

    def export_data(self, db_obj):
        self.get_set_query_data(db_obj.query_date_compare)
        self.insert_db_row(db_obj.store_row)

    def insert_db_row(self, db_insertion_function):
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

        db_insertion_function(self.table_name, [", ".join(column_list), ", ".join(value_list)])

    def build_query_str(self): #This function must be impleneted
        raise NotImplementedError()

    def get_set_query_data(self, db_query_function):
        query_str = self.build_query_str()
        compare_str = "disk_use_percent, last_access_average"

        query_data = db_query_function(self.table_name, query_str, compare_str)

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


    def get_old_file_list(self, minimum_day_num):
        flaged_files = []
        for file_tuple in self.file_list:
            if file_tuple.last_access > minimum_day_num:
                flaged_files.append(file_tuple.file_path)

        return flaged_files

    def calculate_stats(self):
        self.get_total_space()
        self.get_disk_use_percentage()
        self.get_access_average()

