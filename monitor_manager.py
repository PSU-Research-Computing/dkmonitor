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

        #Checks for cleaning routines
        self.check_clean()

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
        print("Total time: {t}".format(t=total))
        print('----')
        print("Done. Exporting data To database...")
        dk_stat_obj.export_data(self.database) #Exports data from dk_stat_obj to the database
        print("Done. Emailing Users")
        #Emails users with bad data
        if dk_stat_obj.get_disk_use_percent() > task["Disk_Use_Threshold"]: #TODO Implement Use threshold
            dk_stat_obj.email_users(self.emailer, #Emails users
                                    self.settings["Email_API"]["User_postfix"],
                                    task["Last_Access_Threshold"],
                                    task["Days_Between_Runs"],
                                    task["File_Relocation_Path"],
                                    task["Bad_flag_percent"])
        print("Done")


    def run_task(self, task_name):
        task = self.settings["Scheduled_Tasks"][task_name]
        dk_stat_obj = dk_stat.dk_stat(task["System_name"], task["Directory_Path"]) #Instanciates the disk statistics object
        dk_stat_obj.dir_search() #Searches the Directory 
        dk_stat_obj.export_data(self.database) #Exports data from dk_stat_obj to the database
        if dk_stat_obj.get_disk_use_percent() > task["Disk_Use_Threshold"]: #TODO Implement Use threshold
            dk_stat_obj.email_users(self.emailer, #Emails users
                                    self.settings["Email_API"]["User_postfix"],
                                    task["Last_Access_Threshold"],
                                    task["Days_Between_Runs"],
                                    task["File_Relocation_Path"],
                                    task["Bad_flag_percent"])


    #Runs all tasks in the json settings file
    def run_tasks(self):
        for task in self.settings["Scheduled_Tasks"].keys():
            self.run_task(task)

    def run_tasks_time(self):
        for task in self.settings["Scheduled_Tasks"].keys():
            self.run_task_time(task)

    def check_clean(self):
        for task in self.settings["Scheduled_Tasks"].keys():
            if task["File_Relocation_Path"] != "":
                query_str = build_query_str(task)
                collumn_names = "*"
                query_data = self.database.query_date_compare(query_str, collumn_names, "directory_stats")
                if query_data != None:
                    self.clean_disk(task["Directory_Path"], task["File_Relocation_Path"])

    def clean_disk(self, directory, relocation_path):
        pass

    def build_query_str(self, task_name):
        task = self.settings["Scheduled_Tasks"][task_name]
        query_str = "disk_use_percent > '{dkp}' AND searched_directory = '{sdir}' AND system = '{sys}'"
        query_str = query_str.format(dkp=task["Disk_Use_Threshold"],
                                     sdir=task["Directory_Path"],
                                     sys=task["System_name"])

        return query_str




if __name__ == "__main__":
    mon_man = Monitor_manager()
    mon_man.run_tasks_time()

