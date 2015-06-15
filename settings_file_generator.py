import json

def generate_json(file_name):
    task_dict = {"Directory_Path" : "", "Days_Between_Runs" : 30, "Email_Users" : ""}
    db_dict = {"User_name" : "", "Password" : "", "DataBase" : ""}
    email_dict = {"User_name" : "", "Password" : ""}
    data_dict = {
            "Scheduled_Tasks" : {"Scratch" : task_dict, "Scratch2" : task_dict},
            "Database_info" : db_dict,
            "Email_API" : email_dict
            }

    with open(file_name, 'w') as jfile:
        json.dump(data_dict, jfile)

if __name__ == "__main__":
    generate_json("settings.json")
