import json
import os
import getpass
from pwd import getpwuid

class dir_purge:

    def __init__(self, directory):
        self.user = getpass.getuser()
        self.search_dir = ""
        try:
            os.path.isdir(directory)
            self.search_dir = directory
        except:
            raise Exception("Directory path {dir} is incorrect".format(dir=directory))

    def delete_old_files(self, age, recursive_dir=None, move_dir=None):
        if recursive_dir == None:
            self.delete_old_files(age, recursive_dir=self.search_dir)
            
        else:
            if os.path.isdir(recursive_dir):
                content_list = os.listdir(recursive_dir)
                for i in content_list:
                    current_path = recursive_dir + '/' + i
                    if os.path.isfile(current_path):
                        if self.name == getpwuid(os.stat(current_path).st_uid).pw_name:
                            last_access = (time.time() - os.path.getsize(current_path)) / 86400
                            if last_access >= age: #If current files's last access is greater than age
                                os.remove(current_path) #remove file 

            else:
                try:
                    self.delete_old_files(age, recursive_dir=(current_path))
                except OSError:
                    pass

    def delete_big_files(self, max_size, recursive_dir=None, move_dir=None):
        if recursive_dir == None:
            self.delete_big_files(max_size, recursive_dir=self.search_dir)
        else:
            if os.path.isdir(recursive_dir):
                content_list = os.listdir(recursive_dir)
                for i in content_list:
                    current_path = recursive_dir + '/' + i
                    if os.path.isfile(current_path):
                        if self.name == getpwuid(os.stat(current_path).st_uid).pw_name:
                            file_size = int(os.path.getsize(current_path))
                            if file_size >= max_size: #If current files's last access is greater than age
                                os.remove(current_path) #remove file 

            else:
                try:
                    self.delete_big_files(max_size, recursive_dir=(current_path))
                except OSError:
                    pass



