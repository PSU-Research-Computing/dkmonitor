"""
This script contains the class dk_clean.
dk_clean is used to move all old files from one directory to another
"""

import re, time, shutil, pwd
import threading, queue

import sys, os
sys.path.append(os.path.abspath("../.."))

from dkmonitor.utilities import log_setup
from dkmonitor.utilities.dir_scan import dir_scan
from dkmonitor.utilities.dk_stat import get_disk_use_percent
from dkmonitor.config.settings_manager import export_settings

class ConflictingSettingsError(Exception):
    """Error for when relocation path and delete files are both set is not found"""
    def __init__(self, message):
        super(ConflictingSettingsError, self).__init__(message)


class DkClean:
    """The class dk_clean is used to move old files from one directory to an other.
    The process can be run with multithreading or just iterativly"""

    def __init__(self, task):
        self.task = task
        self.thread_settings = export_settings()["Thread_Settings"]

        self.que = queue.PriorityQueue()
        self.permission_error_que = queue.PriorityQueue()
        self.full_disk_que = queue.PriorityQueue()

        self.logger = log_setup.setup_logger(__name__)

    def build_file_que(self):
        """Adds old file paths to a thread safe que"""
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
            if err.errno == 13:
                self.permission_error_que.put(file_path)
            if err.errno == 28: #Disk full
                if self.task["delete_when_full"] is True:
                    self.delete_file(file_path)
                else:
                    self.full_disk_que.put(file_path)
                    raise err

    def delete_file(self, file_path):
        """Deletes file"""
        try:
            os.remove(file_path)
        except IOError as err:
            if err.errno == 13:
                self.permission_error_que.put(file_path)

    def create_file_tree(self, uid, path):
        """Creates file tree after move_to with user ownership"""
        path = path.replace(self.task["relocation_path"], "")
        directory = path.split("/")
        current_path = self.task["relocation_path"]
        for direct in directory:
            try:
                new_dir = os.path.join(current_path, direct)
                os.mkdir(new_dir)
                os.chown(new_dir, uid, uid)
            except OSError:
                pass
            current_path = new_dir

    #MULTI-THREADING######################################
    def worker(self, clean_function):
        """Worker Function"""
        while True:
            path = self.que.get()
            clean_function(path[1])
            self.que.task_done()

    def build_pool(self, clean_function):
        """Builds Pool of thread workers"""
        for _ in range(self.thread_settings["thread_number"]):
            thread = threading.Thread(target=self.worker, args=(clean_function,))
            thread.daemon = True
            thread.start()

    def clean_disk_threaded(self, clean_function):
        """Starts the threaded cleaning routine"""
        self.build_pool(clean_function)
        self.build_file_que()
        self.que.join()

        self.log_file_errors()

    #ITERATIVE###########################################
    def clean_disk_iterative(self, clean_function):
        """Cleans disk iteratively"""
        self.build_file_que()
        while not self.que.empty():
            file_path = self.que.get()
            clean_function(file_path[1])

        self.log_file_errors()

    def log_file_errors(self):
        """Logs number of files that could not be moved or deleted"""
        if len(self.permission_error_que) > 0:
            self.logger.error("Permissions error on %s files.", len(self.permission_error_que))
        if len(self.full_disk_que) > 0:
            self.logger.error("Relocation_Path disk full. %s files could not be moved",
                              len(self.full_disk_que))



def check_then_clean(task):
    """
    Checks weather the disk should be cleaned based on task settings
    and runs the correct routine (iterative/multithreaded
    """
    if (task["relocation_path"] != "") or (task["delete_old_files"] is True):
        print("Checking if disk: '{}' needs to be cleaned".format(task["target_path"]))

        disk_use = get_disk_use_percent(task["target_path"])
        if disk_use > task["usage_critical_threshold"]:
            clean_obj = DkClean(task)
            if task["relocation_path"] != "":
                clean_function = clean_obj.move_file
            elif task["delete_old_files"] is True:
                clean_function = clean_obj.delete_file
            else:
                raise ConflictingSettingsError(("Error both relocation_path ",
                                                "and delete_old_files are set"))
            if clean_obj.thread_settings["thread_mode"] == 'yes':
                clean_obj.clean_disk_threaded(clean_function)
            else:
                clean_obj.clean_disk_iterative(clean_function)
        else:
            print("Disk: '{}' does not need to be cleaned".format(task["target_path"]))
