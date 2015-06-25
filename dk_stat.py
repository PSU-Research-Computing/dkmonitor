import os
import time
from pwd import getpwuid
import operator
from collections import namedtuple
import datetime

import user_obj
import dir_obj
import db_interface


#User = namedtuple('User', 'tota_size use_percent average_access old_file_list')
#Db_values = namedtuple('Db_values', 'tota_file_size disk_use_percent last_average_access')
#User2 = namedtuple('User', 'db_values old_file_list')

#User = namedtuple('User', 'tota_size use_percent average_access')
file_tuple = namedtuple('file_tuple', 'file_path file_size last_access')

class dk_stat:

    def __init__(self, system, search_dir):

        #Input search directory path verification exception
        try:
            os.listdir(search_dir)
        except:
            raise Exception("Directory path: {dir} is invalid.".format(dir=search_dir))

        self.search_time = 0
        self.user_hash = {}
        self.directory_obj = None
        self.system = system
        self.search_directory = search_dir
        #self.load_users_file("../user_txt_file2.txt")
        #print("Loaded")


    def dir_search(self, recursive_dir=None): #possibly divide into multiple fucntions

        if recursive_dir == None:
            self.search_time = datetime.datetime.now()
            self.directory_obj = dir_obj.Directory(search_dir=self.search_directory,
                                                   system=self.system,
                                                   datetime=self.search_time) #Creates dir_obj

            self.dir_search(recursive_dir=self.search_directory) #starts recursive call

        else:
            if os.path.isdir(recursive_dir):
                content_list = os.listdir(recursive_dir)
                for i in content_list:
                    try:
                        self.dir_search(recursive_dir=(recursive_dir + '/' + i)) #recursive call on every item
                    except OSError:
                        pass

            if os.path.isfile(recursive_dir): #If the source dir is a file then check to see when it was modified
                last_access = (time.time() - os.path.getatime(recursive_dir)) / 86400 #divide CPU time into days
                file_size = os.path.getsize(recursive_dir)
                int(file_size)

                file_tup = file_tuple(recursive_dir, file_size, last_access)
                self.directory_obj.add_file(file_tup) #Add file to directory obj

                name = getpwuid(os.stat(recursive_dir).st_uid).pw_name #gets user name 
                if name not in self.user_hash.keys(): #if name has not already be found then add to user_hash
                    self.user_hash[name] = user_obj.User(name,
                                                         search_dir=self.search_directory,
                                                         system=self.system,
                                                         datetime=self.search_time)
                self.user_hash[name].add_file(file_tup)

    def export_data(self, db_obj):
        self.directory_obj.export_data(db_obj)
        for user in self.user_hash.keys():
            self.user_hash[user].export_data(db_obj)

    def email_users(self,
                    emailer_obj,
                    postfix,
                    access_day_threshold,
                    file_size_threshold,
                    percentage_threshold):

        for user in self.user_hash.keys():
            self.user_hash[user].email_user(emailer_obj,
                                            postfix,
                                            access_day_threshold,
                                            file_size_threshold,
                                            percentage_threshold)


    #Utility Functions##########################
    def save_users_to_file(self):
        with open("../user_txt_file2.txt", 'w') as ufile:
            for user in self.user_hash.keys():
                ufile.write(self.user_hash[user].save_data() + '\n')

    def save_dir_to_file(self):
        with open("../dir_txt_file.txt", 'w') as dfile:
           dfile.write(self.directory_obj.save_data() + '\n')

    def load_users_file(self, file_tuple_name):
        with open(file_tuple_name, 'r') as ufile:
            for line in ufile:
                dilim_list = line[:-1].split(" ")
                self.user_hash[dilim_list[0]] = user_obj.User(dilim_list[0],
                                                              search_dir=str(dilim_list[3]),
                                                              datetime=dilim_list[1],
                                                              total_file_size=float(dilim_list[4]),
                                                              use_percent=float(dilim_list[5]),
                                                              average_access=float(dilim_list[6]),
                                                              use_percent_change=0.0,
                                                              avrg_access_change=0.0)

    def load_dir_obj(self, file_tuple_name):
        with open(file_tuple_name, 'r') as dfile:
            line = dfile.readline()
            dilim_list = line[:-1].split(" ")
            print (dilim_list[5])
            self.directory_obj = dir_obj.Directory(datetime=dilim_list[0],
                                                   search_dir=dilim_list[2],
                                                   total_file_size=dilim_list[3],
                                                   use_percent=float(dilim_list[4]),
                                                   average_access=float(dilim_list[5]),
                                                   use_percent_change=0.0,
                                                   avrg_access_change=0.0)



if __name__ == "__main__":
    dk1 = dk_stat("/disk/scratch", "hecate")
    #dk1.dir_search();
    db = db_interface.data_base('dkmonitor', 'root', '')
    dk1.load_users_file("../user_txt_file3.txt")
    dk1.load_dir_obj("../dir_txt_file1.txt")
    dk1.export_data(db)

    """
    print ("writing file")
    dk1.save_users_to_file()
    dk1.save_dir_to_file()
    """



