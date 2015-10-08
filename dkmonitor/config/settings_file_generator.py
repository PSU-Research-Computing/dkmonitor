import os
import json
import argparse
import configparser


class EnvironmentVariableNotSetError(Exception):
    def __init__(self, message):
        super(ConfigurationFilesNotFoundError, self).__init__(message)
def build_configs(option_file):
    """Builds The configparser objects based on options set in a json file"""

    try:
        with open(option_file, "r") as jfile:
            option_list = json.load(jfile)
    except OSError as err:
        print("ERROR: settings_configurations.json not found. Settings files cannot be generated")
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

def generate_task_config(save_path, file_name, config_dict):
    """Generates a single task config file"""

    task_config = config_dict["task"] #TODO check for .cfg at the end
    print(task_config)
    with open(save_path + '/' + file_name, 'w') as tconf:
        task_config.write(tconf)

def get_args():
    """Gets args from argparse"""

    parser = argparse.ArgumentParser(description="")

    subparser = parser.add_subparsers()
    default_parser = subparser.add_parser("default")
    default_parser.set_defaults(which="default")

    file_parser = subparser.add_parser("file_name")
    file_parser.set_defaults(which="file_name")
    file_parser.add_argument("file_name", help="Name of the config file you want save in the default location")

    path_parser = subparser.add_parser("full_path")
    path_parser.set_defaults(which="full_path")
    path_parser.add_argument("full_path", help="Full path (including file name) of where you want to save the config file")
    return parser.parse_args()

def main():
    """Runs command line interface and checks arguments"""

    args = get_args()
    print(args.which)
    if args.which == "default":
        print("asdf")
        try:
            conf_path = os.environ["DKM_CONF"]
            generate_task_config(conf_path + "/tasks", "new_config.cfg", build_configs("settings_configurations.json"))
        except KeyError:
            raise EnvironmentVariableNotSetError("ERROR: DKM_CONF environment variable not set, file not created")
    elif args.which == "file_name":
        try:
            conf_path = os.environ["DKM_CONF"]
            if not args.file_name.endswith(".cfg"):
                args.file_name += ".cfg"
            generate_task_config(conf_path + '/tasks', args.file_name, build_configs("settings_configurations.json"))
        except KeyError:
            raise EnvironmentVariableNotSetError("ERROR: DKM_CONF environment variable not set, file not created")
    elif args.which == "full_path":
        base_path = args.full_path[:args.full_path.rfind("/")]
        file_name = args.full_path[args.full_path.rfind("/"):]
        if not file_name.endswith(".cfg"):
            file_name += ".cfg"
        try:
            generate_task_config(base_path, file_name, build_configs("settings_configurations.json"))
        except OSError:
            print("ERROR: Path Given is incorrect")



if __name__ == "__main__":
    main()

