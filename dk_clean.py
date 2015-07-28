import os
import re
import time
from pwd import getpwuid

import threading
from queue import Queue

class dk_clean:
    def __init__(self, search_dir, move_to, access_threshold):
        self.search_dir = search_dir
        self.move_to = move_to
        self.access_threshold = access_threshold
        self.que = Queue()


    #Worker Function
    def worker(self):
        while True:
            path = self.que.get()
            self.move_file(path)
            self.que.task_done()

    #Builds Pool of thread workers
    def build_pool(self, thread_number):
        for i in range(thread_number):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()

    #Builds queue of old files to be moved
    def build_file_que(self, recursive_dir):
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
                    except OSError:
                        pass

    #Moves all files with multithreading
    def move_all_threaded(self, thread_number):
        self.build_pool(thread_number)
        self.build_file_que(self.search_dir)
        self.que.join() #waits for threads to finish

    #Moves all files sequentailly
    def move_all(self):
        self.build_file_que()
        self.process_que()

    #Moves all files in queue sequentailly
    def process_que(self):
        while not self.que.empty():
            file_path = self.que.get()
            self.move_file(file_path)

    #Moves individual file while still preseving its file path
    def move_file(self, file_path):
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
