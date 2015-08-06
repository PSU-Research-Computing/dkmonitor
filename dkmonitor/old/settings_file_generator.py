"""
This file is meant to be used to generate a new settings file
"""

import json

def generate_json(file_name):
    """This function generates a json settings file"""

    task_dict = {"System_name" : "Circe",
                 "Directory_Path" : "/disk/scratch",
                 "File_Relocation_Path" : "/tmp",
                 "Days_Between_Runs" : 1,
                 "Last_Access_Threshold" : 14,
                 "Bad_flag_percent" : 25.0,
                 "Disk_Use_Percent_Threshold" : 40.0,
                 "Email_Users" : "yes"}

    db_dict = {"User_name" : "",
               "Password" : "",
               "DataBase" : "diskspace_monitor",
               "Host" : "pgsql.rc.pdx.edu",
               "Purge_After_Day_Number" : 30}

    email_dict = {"User_postfix" : "pdx.edu"}

    thread_dict = {"Thread_Mode" : "yes",
                   "Thread_Number" : 5}

    data_dict = {"Scheduled_Tasks" : {"Scratch" : task_dict},
                 "Thread_Settings" : thread_dict,
                 "DataBase_info" : db_dict,
                 "Email_API" : email_dict}

    with open(file_name, 'w') as jfile:
        json.dump(data_dict, jfile, indent=4, separators=(",", ":"))

if __name__ == "__main__":
    generate_json("settings.json")