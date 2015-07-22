import json
import db_interface
import dk_stat
import settings_obj
import dk_emailer
import time

class Monitor_manager(settings_obj.Settings_interface):

    def __init__(self):
        settings_obj.Settings_interface.__init__(self)

        #Configures Email api
        self.emailer = dk_emailer.emailer(self.settings["Email_API"]["User_name"],
                                          self.settings["Email_API"]["Password"],
                                          self.settings["Email_API"]["User_postfix"])

        #Configures database
        self.database = db_interface.data_base(self.settings["DataBase_info"]["DataBase"],
                                               self.settings["DataBase_info"]["User_name"],
                                               self.settings["DataBase_info"]["Password"],
                                               self.settings["DataBase_info"]["Host"])

    #Rus a single task from the settings json file loaded
    def run_task_time(self, task_name):
        task = self.settings["Scheduled_Tasks"][task_name]
        dk_stat_obj = dk_stat.dk_stat(task["System_name"], task["Directory_Path"]) #Instanciates the disk statistics object
        print("Searching {path}".format(path=task["Directory_Path"]))
        start = time.time()
        dk_stat_obj.dir_search() #Searches the Directory 
        end = time.time()
        total = end - start
        print('----')
        print(total)
        print('----')
        print("Done. Exporting data To database...")
        dk_stat_obj.export_data(self.database) #Exports data from dk_stat_obj to the database
        print("Done. Emailing Users")
        #Emails users with bad data
        dk_stat_obj.email_users(self.emailer,
                                self.settings["Email_API"]["User_postfix"],
                                task["Email_flags"]["Access_day_threshold"],
                                task["Email_flags"]["Total_file_size_threshold"],
                                task["Email_flags"]["Use_percentage_threshold"])
        print("Done")


    def run_task(self, task_name):
        task = self.settings["Scheduled_Tasks"][task_name]
        dk_stat_obj = dk_stat.dk_stat(task["System_name"], task["Directory_Path"]) #Instanciates the disk statistics object
        dk_stat_obj.dir_search() #Searches the Directory 
        dk_stat_obj.export_data(self.database) #Exports data from dk_stat_obj to the database
        if dk_stat_obj.get_disk_use_percent > task["Disk_Use_Threshold"]: #TODO Implement Use threshold
            dk_stat_obj.email_users(self.emailer, #Emails users
                                    self.settings["Email_API"]["User_postfix"],
                                    task["Bad_flag_percent"])


    #Runs all tasks in the json settings file
    def run_tasks(self):
        for task in self.settings["Scheduled_Tasks"].keys():
            self.run_task(task)

    def schedule_clean(self):
        pass

    def clean_disk(self):
        pass


if __name__ == "__main__":
    mon_man = Monitor_manager()
    mon_man.run_tasks()

