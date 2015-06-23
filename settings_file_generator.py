import json

def generate_json(file_name):
    flag_dict = {"Access_day_threshold" : 30,
                 "Total_file_size_threshold" : 500,
                 "Use_percentage_threshold" : 5}

    task_dict = {"System_name" : "",
                 "Directory_Path" : "",
                 "Days_Between_Runs" : 30,
                 "Email_Users" : "",
                 "Email_flags" : flag_dict}

    db_dict = {"User_name" : "",
               "Password" : "",
               "DataBase" : ""}

    email_dict = {"User_name" : "",
                  "Password" : "",
                  "User_postfix" : ""}

    data_dict = {"Scheduled_Tasks" : {"Scratch" : task_dict, "Scratch2" : task_dict},
                 "Database_info" : db_dict,
                 "Email_API" : email_dict}

    with open(file_name, 'w') as jfile:
        json.dump(data_dict, jfile, indent=4, separators=(",", ":"))

if __name__ == "__main__":
    generate_json("settings.json")
