import json
import db_interface
import dk_stat
import monitor_manager

class Cmd_interface(monitor_manager.Monitor_manager):

    def __init__(self):
        monitor_manager.Monitor_manager.__init__(self)

    def list_tasks(self):
        print ("Scheduled Tasks: ##############")
        for task in self.settings["Scheduled_Tasks"]:
            for field in task.items():
                print (field + " " + task[field])

            print ("")

    def run_scheduled_task(self):
        pass

    def create_run_task(self):
        pass

    def create_save_task(self):
        pass

    def display_task_stats(self, task_name):
        pass

    def email_flagged_users(self):
        pass


if __name__ == "__main__":
    pass

