import psycopg2
import inspect
import json
import glob

import configparser
from configparser import NoOptionError
from configparser import NoSectionError

import sys, os
sys.path.append(os.path.abspath("../.."))

from dkmonitor.utilities.field_lists import FieldLists
from dkmonitor.utilities.log_setup import setup_logger
from dkmonitor.utilities.config_checker import ConfigChecker

class ConfigReader():
    def __init__(self):
        self.logger = setup_logger("settings_log.log")
        try:
            self.config_root = os.environ["DKM_CONF"]
        except KeyError as err:
            self.logger.critical("No configuration files found, DKM_CONF not set")
            print("ERROR: ***No Configuration files found***")
            raise err

        self.task_config = configparser.ConfigParser()
        self.gen_config = configparser.ConfigParser()
        self.config_dict = {"task": configparser.ConfigParser(), "general": configparser.ConfigParser()}

        #self.conf_checker = ConfigChecker()


        #with open("settings_configurations.json") as json_f:
            #self.option_data = json.load(json_f)

    def verify_option(self, option):
        good_flag = True

        try:
            otype = option["type"]
            if otype == "bool":
                self.verify_boolean_field(self.config_dict[option["config_type"]], option)
            elif otype == "int":
                self.check_log_set_int(self.config_dict[option["config_type"]], option)
            elif otype == "path":
                good_flag = self.verify_path_field(self.config_dict[option["config_type"]], option)
            elif otype == "str":
                good_flag = self.verify_str_field(self.config_dict[option["config_type"]], option)

        except NoSectionError:
            if option["error"] == "critical":
                self.logger.critical("The section %s does not exist", option["section_name"])
                good_flag = False
            else:
                self.logger.error("The section %s does not exist, this could cause problems", option["section_name"])

        except NoOptionError:
            if option["error"] == "critical":
                self.logger.critical("The option %s in section %s does not exist. Program cannot run", option["option_name"], option["section_name"])
                good_flag = False
            else:
                self.logger.warning("Option %s was not found. Setting to default", option["option_name"])
                self.config_dict["config_type"].set(option["section_name"], option["option_name"], option["default_value"])

        return good_flag


    def verify_options(self):
        try:
            with open("settings_configurations.json", "r") as jfile:
                option_list = json.load(jfile)

            self.config_dict["general"].read(self.config_root + "/general_settings.cfg")
            task_flags = {}
            gen_flags = []
            for option in option_list:
                if option["config_type"] == "task":
                    task_files = self.read_tasks()
                    for task_file in task_files:
                        self.config_dict["task"].read(task_file)
                        if task_file not in task_flags.keys():
                            task_flags[task_file] = [self.verify_option(option)]
                        else:
                            task_flags[task_file].append(self.verify_option(option))
                else:
                    gen_flags.append(self.verify_option(option))

            if False in gen_flags:
                self.logger.critical("Too many issues in general_settings configuartion file. Program halting")

            for key, flag_list in list(task_flags.items()):
                if False in flag_list:
                    del task_flags[key]
                    self.logger.error("Too many issues in configuration file %s. Skipping task.", key)

        except OSError:
            self.logger.critical("Cannot find the settings_configuration json file to check configurations")



    #Task settings file(s) read functions
    def read_tasks(self):
        task_root = self.config_root + "/tasks/"
        try:
            #task_files = os.listdir(task_root)
            task_files = glob.glob(task_root + "/*.cfg")
        except OSError as err:
            self.logger.critical("No tasks directory found in DKM_CONF")
            raise err

        #return [task_root + task for task in task_files]
        return task_files


    def read_task(self, task_file):
        self.task_config.read(task_file)


    def verify_path_field(self, config, option):
        good_flag = True
        path = config.get(option["section_name"], option["option_name"])
        good_flag = self.verify_str_field(config, option)
        if not os.path.exists(path):
            if option["error"] == "warning":
                self.logger.warning("The path field %s in section: %s does not exist", option["option_name"], option["section_name"])
                good_flag = True
            elif option["error"] == "critical":
                self.logger.error("The path field %s in section: %s does not exist", option["option_name"], option["section_name"])
                good_flag = False

        if option["error"] == "warning":
            return True
        return good_flag

    def verify_str_field(self, config, option):
        good_flag = True
        string = config.get(option["section_name"], option["option_name"])
        if string == "":
            if option["error"] == "warning":
                self.logger.warning("The field %s in section: %s is not set", option["option_name"], option["section_name"])
            if option["error"] == "critical":
                self.logger.error("The field %s in section: %s is not set", option["option_name"], option["section_name"])
                self.logger.error("Program aborting")
                good_flag = False
            good_flag = False

        if option["error"] == "warning":
            return True
        return good_flag

    def verify_boolean_field(self, config, option):
        """
        Verifies a boolean field
        If input in field is in the incorrect format:
        the field is set to default
        """

        good_flag = True
        try:
            bool_val = config.getboolean(option["section_name"], option["option_name"])
            if bool_val is True:
                config.set(option["section_name"], option["option_name"], "yes")

        except ValueError:
            self.logger.warning("The %s flag set in: %s must be a boolean value "
                                "(yes/no, true/false, on/off, 1/0)", option["option_name"], option["section_name"])
            self.logger.warning("Setting %s flag to: '%s'")
            config.set(option["section_name"], option["option_name"], option["default_value"])

        return good_flag


    def verify_int_field(self, config, option):
        int_val = False
        try:
            int_val = config.getint(option["section_name"], option["option_name"])
        except ValueError:
            self.logger.warning("The %s set in %s must be an integer", option["option_name"], option["section_name"])
            self.logger.warning("Setting %s to default value: %s", option["option_name"], option["default_value"])
            config.set(option["section_name"], option["option_name"], option["default_value"])

        return int_val

    def check_log_set_int(self, config, option):

        value = self.verify_int_field(config, option)
        if (option["mininum"] != "") and (option["maximum"] != ""):
            if value not in range(int(option["mininum"]), int(option["maximum"])):
                self.logger.warning("The %s set in %s must be an integer between %s and %s",
                                    option["option_name"],
                                    option["section_name"],
                                    option["mininum"],
                                    option["maximum"])
                self.logger.warning("Setting %s to default value: %s", option["option_name"], option["default_value"])
                config.set(option["section_name"], option["option_name"], option["default_value"])

        elif (option["mininum"] != ""):
            if value < int(option["mininum"]):
                self.logger.warning("%s field in: %s must be an integer bigger than %s",
                                    option["option_name"],
                                    option["section_name"],
                                    option["mininum"])
                self.logger.warning("Setting %s to defualt value: %s", option["option_name"], option["default_value"])
                config.set(option["section_name"], option["option_name"], option["default_value"])

        return value

    def config_to_dict(self, config, section):
        """Converts parsed config file to dictionary format"""

        add_dict = dict(config.items(section))
        for field in add_dict.keys():
            if add_dict[field].isdigit():
                add_dict[field] = int(add_dict[field])

        return add_dict


    def read_system_settings(self):
        pass

    def read_scan_settings(self):
        pass

    def read_threshold_settings(self):
        pass

    def read_task_email_settings(self):
        pass

    #General settings file read functions
    def read_general(self):
        pass

    def read_db_settings(self):
        pass

    def read_thread_settings(self):
        pass

    def read_general_email_settings(self):
        pass


if __name__ == "__main__":
    test = ConfigReader()
    test.verify_options()
