import os
import time

import threading
from queue import Queue

class dk_clean:
    def __init__(self, search_dir, move_to, access_threshold, thread_number=0):
        self.search_dir = search_dir
        self.move_to = move_to
        self.access_threshold = access_threshold
        self.thread_number = thread_number
        self.que = Queue()


    def worker(self):
        while True:
            path = self.que.get()
            self.move_file(path)
            self.que.task_done()

    def build_pool(self):
        for i in range(self.thread_number):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()


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

    def move_all_threaded(self):
        self.build_pool()
        self.build_file_que(self.search_dir)
        self.que.join()

    def move_all(self):
        self.build_file_que()
        self.process_que()

    def process_que(self):
        while not self.que.empty():
            file_path = self.que.get()
            self.move_file(file_path)


    def move_file(self, file_path):
        print("Moving_file {f}".format(f=file_path))
