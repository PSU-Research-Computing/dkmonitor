import configparser
import json
import os

def build_configs(option_file):
    """Builds The configparser objects based on options set in a json file"""

    try:
        with open(option_file, "r") as jfile:
            option_list = json.load(jfile)
    except OSError as err:
        raise err

    config_dict = {}
    for option in option_list:
        if not option['config_type'] in config_dict.keys():
            config_dict[option["config_type"]] = configparser.ConfigParser()
        try:
            config_dict[option["config_type"]].add_section(option["section_name"])
        except configparser.DuplicateSectionError:
            pass

        config_dict[option["config_type"]].set(option["section_name"],
                                               option["option_name"],
                                               option["default_value"])

    return config_dict

def generate_config_files(path_to_config_dir, path_to_settings_file):
    """Writes the configparser objects to files"""

    config_dict = build_configs(path_to_settings_file)
    try:
        os.makedirs(path_to_config_dir + "/tasks/")
    except OSError:
        pass

    task_config_path = path_to_config_dir + "/tasks/"
    for key, config in list(config_dict.items()):
        if key == "task":
            with open(task_config_path + "task_example.cfg", 'w') as tconf:
                config.write(tconf)
        else:
            with open(path_to_config_dir + "/" + key + ".cfg", 'w') as conf:
                config.write(conf)



if __name__ == "__main__":
    generate_config_files("/home/wpatt2/ARC/Scratch_moniter/Dkm_config_log/test/")

