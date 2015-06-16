import json
import db_interface
import dk_stat
import settings_obj
import dk_emailer

class Monitor_manager(settings_obj.Settings_interface):

    def __init__(self):
        settings_obj.Settings_interface.__init__(self)

        self.emailer = dk_emailer.emailer(
                self.settings["Email_API"]["User_name"],
                self.settings["Email_API"]["Password"],
                self.settings["Email_API"]["Suffix"])

        self.database = db_interface.data_base(
                self.settings["DataBase_info"]["dbname"],
                self.settings["DataBase_info"]["User_name"],
                self.settings["DataBase_info"]["Password"])

    def run_task(self, task_name):
        task = self.settings["Scheduled_Tasks"][task_name]
        dk_stat_obj = dk_stat.dk_stat(task["System_name"], task["Directory_Path"])
        dk_stat_obj.dir_search()
        dk_stat_obj.export_data(self.database)
        dk_stat_obj.email_users(
                self.emailer,
                task["Email_flags"]["Access_day_threshold"],
                task["Email_flags"]["Total_file_size_threshold"],
                task["Email_flags"]["Use_percentage_threshold"])



    #TODO this might not work
    def run_tasks(self):
        for task in self.settings["Scheduled_Tasks"].keys():
            self.run_task(task)


if __name__ == "__main__":
    mon_man = Monitor_manager()
    mon_man.run_tasks()

