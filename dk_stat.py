import os
<<<<<<< HEAD
=======
import pickle
>>>>>>> 17a4456835421be19dc65b30ce422c284cd8a115
import dill
import time
from pwd import getpwuid
import operator
from collections import namedtuple
import user_obj
import db_interface
import datetime

#User = namedtuple('User', 'tota_size use_percent average_access old_file_list')
#Db_values = namedtuple('Db_values', 'tota_file_size disk_use_percent last_average_access')
#User2 = namedtuple('User', 'db_values old_file_list')

#User = namedtuple('User', 'tota_size use_percent average_access')
User_file = namedtuple('User_file', 'file_path file_size last_access')

class dk_stat:


    def __init__(self, search_dir):

        #Input search directory path verification exception
        """
        try:
            os.listdir(search_dir)
        except:
            raise Exception("Directory path: {dir} is invalid.".format(dir=search_dir))

        self.search_time = 0
        """
        self.search_directory = search_dir
        print("Loading pickle")
        pfile = open("../user_hash_dump.p", "rb")
        self.user_hash = dill.load(pfile)
        pfile.close()
        print("Loaded")
        #self.user_hash = {}


    def dir_search(self, recursive_dir=None): #possibly divide into multiple fucntions

        if recursive_dir == None:
            self.search_time = datetime.datetime.now()
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
                if name in self.user_hash.keys(): #if name has already be found then add to hashed list 
                    self.user_hash[name].add_file(User_file(recursive_dir, file_size, last_access))
                else:                    #else append name list and create a new list in hash with username as the key
                    self.user_hash[name] = user_obj.User(name, search_dir=self.search_directory, datetime=self.search_time)


    def export_users(self, db_obj):
        for user in self.user_hash.keys():
            self.user_hash[user].export_user(db_obj)


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

    def save_users_to_file(self):
        with open("../user_txt_file.txt", 'w') as ufile:
            for user in self.user_hash.keys():
                ufile.write(self.user_hash[user].export_data() + '\n')



if __name__ == "__main__":
    dk1 = dk_stat("/disk/scratch")
<<<<<<< HEAD
    db = db_interface.data_base('dkmonitor', 'root', '')
    dk1.export_users(db)

=======
    print ("searching")
    dk1.dir_search()
    print ("built")
    #dill.dump(dk1.user_hash, open("../user_hash_dump.p", "wb"))
    print ("writing file")
    dk1.save_users_to_file()
>>>>>>> 17a4456835421be19dc65b30ce422c284cd8a115


