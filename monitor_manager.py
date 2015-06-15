import json
import db_interface
import dk_stat
import settings_obj

class Monitor_manager(settings_obj.Settings_interface):

    def __init__(self):
        settings_obj.Settings_interface.__init__(self)

        self.database = db_interface.data_base(
                self.settings["DataBase_info"]["dbname"],
                self.settings["DataBase_info"]["User_name"],
                self.settings["DataBase_info"]["Password"])

    def run_task(self, task_name):
        task = self.settings["Scheduled_Tasks"][task_name]
        dk_stat_obj = dk_stat.dk_stat(task["Directory_Path"])
        dk_stat_obj.search_dir()
        dk_stat_obj.export_data(self.database)


    #TODO this might not work
    def run_tasks(self):
        for task in self.settings["Scheduled_Tasks"].keys():
            self.run_task(task)


if __name__ == "__main__":
    mon_man = Monitor_manager()
    mon_man.run_tasks()

