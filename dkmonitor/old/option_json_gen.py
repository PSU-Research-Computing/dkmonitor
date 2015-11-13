"""
This File is strictly used as a utility to create a json file that
the settings files are built off of
"""

import json

def generate_option_config(file_path, object_number):
    """This function creates a json file with objects that the config files are build off of"""

    option = {"option_name": "",
              "section_name": "",
              "config_type": "",
              "type": "",
              "error": "",
              "default_value": "",
              "mininum": "",
              "maximum": ""}

    option_list = []
    for i in range(object_number):
        option_list.append(option)

    diction = {"options":option_list}

    with open(file_path, "w") as json_f:
        json.dump(option_list, json_f, indent=4, separators=(",", ":"))


if __name__ == "__main__":
    generate_option_config("settings_configurations.json", object_number)
