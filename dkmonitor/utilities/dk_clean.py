"""This script contains the class dk_clean.
dk_clean is used to move all old files from one directory to another"""

import re
import time
import shutil
import pwd

import threading
from queue import PriorityQueue

import sys, os
sys.path.append(os.path.abspath("../.."))
from dkmonitor.utilities import log_setup
from dkmonitor.stat.dir_scan import dir_scan

from dkmonitor.config.settings_manager import export_settings

class DkClean:
    """The class dk_clean is used to move old files from one directory to an other.
    The process can be run with multithreading or just iterativly"""

    def __init__(self, task):
        self.task = task
        self.thread_settings = export_settings()["Thread_Settings"]
        self.que = PriorityQueue()

        self.logger = log_setup.setup_logger(__name__)


    def build_file_que(self):
        print("Moving Files")
        for file_path in dir_scan(self.task["target_path"]):
            last_access = (time.time() - os.path.getatime(file_path)) / 86400
            if last_access > self.task["old_file_threshold"]:
                old_file_size = int(os.path.getsize(file_path))
                priority_num = - (old_file_size * last_access)
                self.que.put((priority_num, file_path))
        print("Done")


    def move_file(self, file_path):
        """Moves individual file while still preseving its file path"""

        uid = os.stat(file_path).st_uid
        user = pwd.getpwuid(uid).pw_name

        root_dir = os.path.join(self.task["relocation_path"],
                                user,
                                self.task["hostname"],
                                self.task["target_path"].replace("/", "_")[1:])

        self.create_file_tree(uid, root_dir)

        new_file_path = re.sub(r"^{old_path}".format(old_path=self.task["target_path"]),
                               root_dir,
                               file_path)

        last_slash = new_file_path.rfind('/')
        dir_path = new_file_path[:last_slash]

        try:
            #self.create_file_tree(uid, dir_path)
            #shutil.move(file_path, new_file_path)
            #print("OLD {o} :: NEW {n}".format(o=file_path, n=new_file_path))
            pass
        except IOError as err:
            if self.task["delete_when_full"] is True:
                os.remove(file_path)
            else:
                raise(err)

    def delete_file(self, file_path):
        """Deletes file"""
        #TODO Throw in some try excpets
        os.remove(file_path)

    def create_file_tree(self, uid, path):
        """Creates file tree after move_to with user ownership"""

        path = path.replace(self.task["relocation_path"], "")
        dirs = path.split("/")
        current_path = self.task["relocation_path"]
        for d in dirs:
            try:
                new_dir = os.path.join(current_path, d)
                os.mkdir(new_dir)
                os.chown(new_dir, uid, uid)
            except OSError:
                pass
            current_path = new_dir


    def clean_disk(self):
        if self.task["relocation_path"] is not None:
            clean_function = self.move_file
        elif self.task["delete_old_files"] is True:
            clean_function = self.delete_file
        else:
            #TODO Raise Error for incorrect settings
            pass
        if self.thread_settings["thread_mode"] == 'yes':
            self.clean_disk_threaded(clean_function)
        else:
            self.clean_disk_iterative(clean_function)

####MULTI-THREADING######################################

    def worker(self, clean_function):
        """Worker Function"""

        while True:
            path = self.que.get()
            clean_function(path[1])
            self.que.task_done()

    def build_pool(self, clean_function):
        """Builds Pool of thread workers"""

        for i in range(self.thread_settings["thread_number"]):
            thread = threading.Thread(target=self.worker, args=(clean_function,))
            thread.daemon = True
            thread.start()

    def clean_disk_threaded(self, clean_function):
        self.build_pool(clean_function)
        self.build_file_que()
        self.que.join()

####ITERATIVE###########################################

    def clean_disk_iterative(self, clean_function):
        self.build_file_que()
        while not self.que.empty():
            file_path = self.que.get()
            clean_function(path[1])


