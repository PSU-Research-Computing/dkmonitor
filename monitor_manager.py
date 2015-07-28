import json
import time
import threading

import db_interface
import dk_stat
import settings_obj
import dk_emailer
import dk_clean

class Monitor_manager(settings_obj.Settings_interface):

    def __init__(self):
        settings_obj.Settings_interface.__init__(self)

        #Configures Email api
        self.emailer = dk_emailer.emailer(self.settings["Email_API"]["User_postfix"])

        #Configures database
        self.database = db_interface.data_base(self.settings["DataBase_info"]["DataBase"],
                                               self.settings["DataBase_info"]["User_name"],
                                               self.settings["DataBase_info"]["Password"],
                                               self.settings["DataBase_info"]["Host"],
                                               self.settings["DataBase_info"]["Purge_After_Day_Number"])

    #Rus a single task from the settings json file loaded
    def run_task(self, task_name):
        task = self.settings["Scheduled_Tasks"][task_name]
        self.check_clean_task(task)
        dk_stat_obj = dk_stat.dk_stat(task["System_name"], task["Directory_Path"]) #Instanciates the disk statistics object
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


    #starts all tasks
    def start(self):
        if self.settings["Thread_Settings"]["Thread_Mode"] == 'yes':
            self.run_tasks_threading()
        else:
            self.run_tasks()

    #Runs all tasks in the json settings file
    def run_tasks(self):
        for task in self.settings["Scheduled_Tasks"].keys():
            self.run_task(task)

    #Runs all tasks in the json settings file with multiple threads
    def run_tasks_threading(self):
        for task in self.settings["Scheduled_Tasks"].keys():
            t = threading.Thread(target=self.run_task, args=(task,))
            t.daemon = False
            t.start()

    #Checks if directory needs to be cleaned
    #Starts cleaning routine if flagged
    def check_clean_task(self, task):
        if task["File_Relocation_Path"] != "":
            query_str = self.build_query_str(task)
            collumn_names = "disk_use_percent"

            query_data = self.database.query_date_compare("directory_stats", query_str, collumn_names)
            if query_data == None:
                pass
            elif query_data[0] > task["Disk_Use_Percent_Threshold"]:
                self.clean_disk(task["Directory_Path"],
                                task["File_Relocation_Path"],
                                task["Last_Access_Threshold"])

    #Cleaning routine function 
    def clean_disk(self, directory, relocation_path, access_threshold):
        print("CLeaning...")
        thread_settings = self.settings["Thread_Settings"]
        clean_obj = dk_clean.dk_clean(directory, relocation_path, access_threshold)
        if thread_settings["Thread_Mode"] == "yes":
            clean_obj.move_all_threaded(thread_settings["Thread_Number"])
        else:
            clean_obj.move_all()

    #Builds query string used to determine if disk needs to be cleaned
    def build_query_str(self, task):
        query_str = "searched_directory = '{sdir}' AND system = '{sys}'"
        query_str = query_str.format(dkp=task["Disk_Use_Percent_Threshold"],
                                     sdir=task["Directory_Path"],
                                     sys=task["System_name"])
        return query_str



if __name__ == "__main__":
    mon_man = Monitor_manager()
    mon_man.start()

