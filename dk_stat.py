import os
import pickle
import time
from pwd import getpwuid
import operator
from collections import namedtuple
from user_obj import User 

#User = namedtuple('User', 'tota_size use_percent average_access old_file_list')
#Db_values = namedtuple('Db_values', 'tota_file_size disk_use_percent last_average_access')
#User2 = namedtuple('User', 'db_values old_file_list')

User = namedtuple('User', 'tota_size use_percent average_access')
User_file = namedtuple('User_file', 'file_path file_size last_access')

class dk_stat:

    def __init__(self, search_dir):

        #Input search directory path verification exception
        """
        try:
            os.listdir(search_dir)
        except:
            raise Exception("Directory path: {dir} is invalid.".format(dir=search_dir))
        """

        self.search_directory = search_dir
        self.file_hash = pickle.load(open("dk_stat_object.p", 'rb')).file_hash
        #self.file_hash = {}


    def dir_search(self, recursive_dir=None): #possibly divide into multiple fucntions

        if recursive_dir == None:
            self.dir_search(recursive_dir = self.search_directory)

        else:
            if os.path.isdir(recursive_dir):
                content_list = os.listdir(recursive_dir)
                for i in content_list:
                    try:
                        self.dir_search(recursive_dir = (recursive_dir + '/' + i)) #recursive call on every item
                    except OSError:
                        pass

            if os.path.isfile(recursive_dir): #If the source dir is a file then check to see when it was modified
                last_access = (time.time() - os.path.getatime(recursive_dir)) / 86400 #divide CPU time into days
                file_size = os.path.getsize(recursive_dir)
                int(file_size)

                name = getpwuid(os.stat(recursive_dir).st_uid).pw_name #get modify time of file 
                if name in self.file_hash.keys(): #if name has already be found then add to hashed list 
                    self.file_hash[name].append(User_file(recursive_dir, file_size, last_access))
                else:                    #else append name list and create a new list in hash with username as the key
                    self.file_hash[name] = [User_file(recursive_dir, file_size, last_access)]

    """
    def get_total_user_space(self): #possibly have optional argument that lets user get output in mb or gb
        user_file_size_dict = {}
        for name in self.file_hash.keys(): #For each user file list in file_hash.
            total_space = 0
            for file in self.file_hash[name]:
                total_space += int(file.file_size)
            user_file_size_dict[name] = total_space #Divide into bytes

        return user_file_size_dict


    def get_disk_use_percentage(self):
        users = self.get_total_user_space()
        percent_dict = {}

        st = os.statvfs(self.search_directory)
        total = st.f_blocks * st.f_frsize

        for user in users.keys():
            user_percentage = 100* float(users[user])/float(total)
            percent_dict[user] = user_percentage

        return percent_dict


    def get_user_access_average(self):
        user_file_access_dict = {}
        for name in self.file_hash.keys():
            total_time = 0
            for count, file in enumerate(self.file_hash[name]):
                total_time += file.last_access

            try: #possibly change this to an if statement
                average_last_access = total_time / count
            except ZeroDivisionError:
                average_last_access = total_time

            user_file_access_dict[name] = average_last_access

        return user_file_access_dict


    #Gets List of files last accessed before 
    def get_old_file_list(self, minimum_day_num):
        old_file_dict = {}
        for user in self.file_hash.keys():
            flaged_files = []
            for file in self.file_hash[user]:
                if file.last_access > minimum_day_num:
                    flaged_files.append(file.file_path)
            old_file_dict[user] = flaged_files

        return old_file_dict


    def get_all_stats(self, minimum_day_num):
        all_stat_dict = {}

        #file_hash = self.dir_search() #disabled. Needs error checking 
        user_space = self.get_total_user_space()
        user_percent = self.get_disk_use_percentage()
        access_averages = self.get_user_access_average()
        #old_user_files = self.get_old_file_list(minimum_day_num)

        for user in self.file_hash.keys():
            user_tuple = User(user_space[user], user_percent[user], access_averages[user]) #fixed this to only have collumns keep an eye out though
            all_stat_dict[user] = user_tuple

        return all_stat_dict
    """

    def format_stat_tuple(self, in_tuple): #TODO I need to add ' marks to string output so that postgres accepts it
        collunm_names = in_tuple._fields
        values = (value for value in in_tuple)
        return [", ".join(collunm_names), ", ".join(values)]

    def generate_db_rows(self): #Probably should change this so it yields sets with as (collumn name, value)
        db_export_dict = self.get_all_stats(30)
        for user in db_export_dict.keys():
            user_db_tuple = db_export_dict[user]
            yield format_stat_tuple(user_db_tuple)

    def format_tuple_query(self, in_tuple, user_name):
        #query_columns = [['user_name', user_name], ["search_directory", self.searched_directory]]
        query_str = "user_name = {name} AND searched_directory = {sdir}".format(name=user_name, sdir=self.searched_directory)
        compare_list = [collumn for collumn in in_tuple._fields[1:]]
        compare_str = ", ".join(compare_list)
        return [query_str, compare_str]

    def generate_query_info(self):
        db_export_dict = self.get_all_stats(30)
        for user in db_export_dict.keys():
            yield format_tuple_query(db_export_dict[user], user)
<<<<<<< HEAD

=======
>>>>>>> User_branch

if __name__ == "__main__":
    dk1 = dk_stat("/disk/scratch")
    #print ("searching")
    #dk1.dir_search()
    #print ("built")
    stats = dk1.get_all_stats(30)


