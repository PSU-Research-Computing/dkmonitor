import json

def generate_json(file_name):
    task_dict = {"System_name" : "",
                 "Directory_Path" : "",
                 "Days_Between_Runs" : 30,
                 "Last_Access_Threshold" : 14,
                 "Bad_flag_percent" : .25,
                 "Disk_Use_Threshold" : .8,
                 "Email_Users" : ""}

    db_dict = {"User_name" : "",
               "Password" : "",
               "DataBase" : "",
               "Host" : ""}

    email_dict = {"User_name" : "",
                  "Password" : "",
                  "User_postfix" : ""}

    data_dict = {"Scheduled_Tasks" : {"Scratch" : task_dict},
                 "DataBase_info" : db_dict,
                 "Email_API" : email_dict}

    with open(file_name, 'w') as jfile:
        json.dump(data_dict, jfile, indent=4, separators=(",", ":"))

if __name__ == "__main__":
    generate_json("settings.json")
