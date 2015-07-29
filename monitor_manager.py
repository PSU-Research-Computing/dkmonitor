"""
This script Is the main managing script for the dk_monitor script suite.
This script is indented to be run as a cron job to monitor actions on any
given disk or directory that is set by the adminstrator
"""

import time
import threading

import db_interface
import dk_stat
import settings_obj
import dk_emailer
import dk_clean

class MonitorManager(settings_obj.Settings_interface):
    """This class is the main managing class for all other classes
    It runs preset tasks that are found in the json settings file"""

    def __init__(self):
        settings_obj.Settings_interface.__init__(self)

        #Configures Email api
        self.emailer = dk_emailer.Emailer(self.settings["Email_API"]["User_postfix"])

        #Configures database
        self.database = db_interface.DataBase(self.settings["DataBase_info"]["DataBase"],
                                              self.settings["DataBase_info"]["User_name"],
                                              self.settings["DataBase_info"]["Password"],
                                              self.settings["DataBase_info"]["Host"],
                                              self.settings["DataBase_info"]["Purge_After_Day_Number"])

    def run_task(self, task_name):
        """Runs a single task from the settings json file loaded"""

        task = self.settings["Scheduled_Tasks"][task_name]
        self.check_clean_task(task)
        #Instanciates the disk statistics object
        dk_stat_obj = dk_stat.DkStat(task["System_name"], task["Directory_Path"])
        print("Searching {path}".format(path=task["Directory_Path"]))
        start = time.time()
        dk_stat_obj.dir_search() #Searches the Directory
        end = time.time()
        total = end - start
        print('----')
        print("Total time: {t}".format(t=total))
        print('----')
        print("Done. Exporting data To database...")
        dk_stat_obj.export_data(self.database) #Exports data from dk_stat_obj to the database
        print("Done. Emailing Users")
        #Emails users with bad data
        if dk_stat_obj.get_disk_use_percent() > task["Disk_Use_Percent_Threshold"]:
            dk_stat_obj.email_users(self.emailer, #Emails users
                                    self.settings["Email_API"]["User_postfix"],
                                    task["Last_Access_Threshold"],
                                    task["Days_Between_Runs"],
                                    task["File_Relocation_Path"],
                                    task["Bad_flag_percent"])
        print("Done")


    def start(self):
        """starts all tasks"""

        if self.settings["Thread_Settings"]["Thread_Mode"] == 'yes':
            self.run_tasks_threading()
        else:
            self.run_tasks()

    def run_tasks(self):
        """Runs all tasks in the json settings file"""
        for task in self.settings["Scheduled_Tasks"].keys():
            self.run_task(task)

    def run_tasks_threading(self):
        """Runs all tasks in the json settings file with multiple threads"""

        for task in self.settings["Scheduled_Tasks"].keys():
            thread = threading.Thread(target=self.run_task, args=(task,))
            thread.daemon = False
            thread.start()

    def check_clean_task(self, task):
        """
        Checks if directory needs to be cleaned
        Starts cleaning routine if flagged
        """

        if task["File_Relocation_Path"] != "":
            query_str = self.build_query_str(task)
            collumn_names = "disk_use_percent"

            query_data = self.database.query_date_compare("directory_stats",
                                                          query_str,
                                                          collumn_names)
            if query_data == None:
                pass
            elif query_data[0] > task["Disk_Use_Percent_Threshold"]:
                self.clean_disk(task["Directory_Path"],
                                task["File_Relocation_Path"],
                                task["Last_Access_Threshold"])

    def clean_disk(self, directory, relocation_path, access_threshold):
        """Cleaning routine function"""

        print("CLeaning...")
        thread_settings = self.settings["Thread_Settings"]
        clean_obj = dk_clean.DkClean(directory, relocation_path, access_threshold)
        if thread_settings["Thread_Mode"] == "yes":
            clean_obj.move_all_threaded(thread_settings["Thread_Number"])
        else:
            clean_obj.move_all()


    #TODO Refactor these functions
    def build_query_str(self, task):
        """Builds query string used to determine if disk needs to be cleaned"""

        query_str = "searched_directory = '{sdir}' AND system = '{sys}'"
        query_str = query_str.format(dkp=task["Disk_Use_Percent_Threshold"],
                                     sdir=task["Directory_Path"],
                                     sys=task["System_name"])
        return query_str



if __name__ == "__main__":
    monitor = MonitorManager()
    monitor.start()

