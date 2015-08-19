import json

def generate_option_config(file_path):
    option = {"option_name": "",
              "type": "",
              "error": "",
              "default_value": "",
              "mininum": "",
              "maximum": ""}

    general = {"DataBase_Settings" : [option for i in range(6)],
               "Thread_Settings" : [option for i in range(2)],
               "Email_Settings" : [option for i in range(2)]}

    task = {"System_Settings" : [option for i in range(2)],
            "Scan_Settings" : [option for i in range(4)],
            "Threshold_Settings" : [option for i in range(3)],
            "Email_Settings" : [option for i in range(3)]}

    configs = {"general": general, "task": task}
    option_list = []
    for i in range(22):
        option_list.append(option)

    diction = {"options":option_list}

    with open(file_path, "w") as sc:
        json.dump(configs, sc, indent=4, separators=(",", ":"))

def generate_option_config2(file_path):
    option = {"option_name": "",
              "section_name": "",
              "config_type": "",
              "type": "",
              "error": "",
              "default_value": "",
              "mininum": "",
              "maximum": ""}

    option_list = []
    for i in range(22):
        option_list.append(option)

    diction = {"options":option_list}

    with open(file_path, "w") as json_f:
        json.dump(option_list, json_f, indent=4, separators=(",", ":"))


if __name__ == "__main__":
    generate_option_config2("settings_configurations.json")
