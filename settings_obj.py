import json
import os
import sys

class Settings_interface():
    def __init__(self):
        self.load_file = "settings.json"
        self.settings = None

        try:
            with open(self.load_file) as jfile:
                self.settings = json.load(jfile)
        except FileNotFoundError as ferror:
            print ("Critical: Json settings file not found")
            raise ferror #probs doesnt work

    def check_settings(self):
        for task_name in self.settings["Scheduled_Tasks"].keys():
            task = self.settings["Scheduled_Tasks"][task_name]
            error_count = 0
            if task["System_name"] == "":
                print("ERROR: No system name for {t}".format(t=task_name))
                error_count += 1
            if not os.path.exists(task["Directory_Path"]):
                print("ERROR: {p} is not a valid path".format(p=task["Directory_Path"]))
                error_count += 1
            #TODO Could be changed to a warning
            if (task["File_Relocation_Path"] != "") and (not os.path.exists(task["File_Relocation_Path"])):
                print("ERROR: {p} is not a valid path".format(p=task["File_Relocation_Path"]))
                error_count += 1

            if error_count > 0:
                sys.exit("Critical Errors, Could not continue")



