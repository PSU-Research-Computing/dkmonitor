"""This script contains the class dk_clean.
dk_clean is used to move all old files from one directory to another"""

import os
import re
import time
from pwd import getpwuid

import threading
from queue import Queue

import log_setup

class DkClean:
    """The class dk_clean is used to move old files from one directory to an other.
    The process can be run with multithreading or just iterativly"""

    def __init__(self, search_dir, move_to, access_threshold):
        self.search_dir = search_dir
        self.move_to = move_to
        self.access_threshold = access_threshold
        self.que = Queue()

        self.logger = log_setup.setup_logger("../log/clean_log.log")

    def build_file_que(self, recursive_dir):
        """Builds queue of old files to be moved"""

        if os.path.isdir(recursive_dir):
            content_list = os.listdir(recursive_dir)
            for i in content_list:
                current_path = recursive_dir + '/' + i
                if os.path.isfile(current_path):
                    last_access = (time.time() - os.path.getatime(current_path)) / 86400
                    if last_access > self.access_threshold:
                        self.que.put(current_path)
                else:
                    try:
                        self.build_file_que(recursive_dir=(current_path))
                    except OSError as oerror:
                        self.logger.info(oerror)

    def move_file(self, file_path):
        """Moves individual file while still preseving its file path"""

        user = getpwuid(os.stat(file_path).st_uid).pw_name
        root_dir = self.move_to + '/' + user
        print("ROOT: " + root_dir)
        #if not os.path.exists(root_dir):
            #os.makedir(root_dir)
        new_file_path = re.sub(r"^{old_path}".format(old_path=self.search_dir), root_dir, file_path)
        last_slash = new_file_path.rfind('/')
        dir_path = new_file_path[:last_slash]
        print("NEW: " + new_file_path)
        #if not os.path.exists(dir_path):
            #os.makedirs(dir_path)
        #shutil.move(file_path, new_file_path)


####MULTI-THREADING######################################
    def worker(self):
        """Worker Function"""

        while True:
            path = self.que.get()
            self.move_file(path)
            self.que.task_done()

    def build_pool(self, thread_number):
        """Builds Pool of thread workers"""

        for i in range(thread_number):
            thread = threading.Thread(target=self.worker)
            thread.daemon = True
            thread.start()

    def move_all_threaded(self, thread_number):
        """Moves all files with multithreading"""

        self.build_pool(thread_number)
        self.build_file_que(self.search_dir)
        self.que.join() #waits for threads to finish

####ITERATIVE###########################################
    def move_all(self):
        """Moves all files sequentailly"""

        self.build_file_que(self.search_dir)
        self.process_que()

    def process_que(self):
        """Moves all files in queue sequentailly"""
        while not self.que.empty():
            file_path = self.que.get()
            self.move_file(file_path)


