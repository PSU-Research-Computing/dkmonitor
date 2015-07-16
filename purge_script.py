import json
import os
import shutil
import getpass
from pwd import getpwuid
import argparse

class dir_purge:

    def __init__(self, directory):
        self.user = getpass.getuser()
        self.search_dir = ""
        try:
            os.path.isdir(directory)
            self.search_dir = directory
        except:
            raise Exception("Directory path {dir} is incorrect".format(dir=directory))

    #TODO Combine these purge functions into one function
    def purge_old_files(self, age, recursive_dir=None, move_dir=None):
        if recursive_dir == None:
            try:
                os.path.isdir(move_dir)
                self.purge_old_files(age, recursive_dir=self.search_dir)
            except OSError:
                raise Exception("Directory to Move files to ({mdir}) is incorrect")

        else:
            if os.path.isdir(recursive_dir):
                content_list = os.listdir(recursive_dir)
                for i in content_list:
                    current_path = recursive_dir + '/' + i
                    if os.path.isfile(current_path):
                        if self.name == getpwuid(os.stat(current_path).st_uid).pw_name:
                            last_access = (time.time() - os.path.getsize(current_path)) / 86400
                            if last_access >= age: #If current files's last access is greater than age
                                if move_dir == None:
                                    os.remove(current_path) #remove file 
                                else:
                                    shutil.move(current_path, move_dir)
                    else:
                        try:
                            self.purge_old_files(age, recursive_dir=(current_path))
                        except OSError:
                            pass

    def purge_big_files(self, max_size, recursive_dir=None, move_dir=None):
        if recursive_dir == None:
            try:
                os.path.isdir(move_dir)
                self.purge_big_files(age, recursive_dir=self.search_dir)
            except OSError:
                raise Exception("Directory to Move files to ({mdir}) is incorrect")

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
                            self.purge_big_files(max_size, recursive_dir=(current_path))
                        except OSError:
                            pass


if __name__ == "__main__":
    descript = """This is a file purging script provided by ARC staff
                  You can use this script to delete all of your
                  old or large files under a specified directory"""
    parser = argparse.ArgumentParser(description=descript)

    parser.add_argument("-s",
                        "--settings_file",
                        dest="settings_file",
                        help="Specify a Json settings file with preconfigured pruge settings")
    parser.add_argument("-m",
                        "--move_to",
                        dest="move_to",
                        help="Specify a directory to move every flagged file to. If not specified, all files will be deleted")
    parser.add_argument("-d",
                        "--purge_directory",
                        dest="purge_directory",
                        help="Specify a directory to purge")
    parser.add_argument("-o",
                        "--old_days_max",
                        dest="old_days_max",
                        help="Purge all files older than the specified amount of days")
    parser.add_argument("-f",
                        "--file_size_max",
                        dest="file_size_max",
                        help="Purge all files large than the specified size (megabytes)")
    parser.add_argument("-i",
                        "--ignore",
                        dest="ignore",
                        help="Ignore all speficied files (in comma separated list)")

    args = parser.parse_args()
