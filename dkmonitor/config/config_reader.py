"""
ConfigReader
"""

import psycopg2
import json
import glob

import configparser
from configparser import NoOptionError
from configparser import NoSectionError

import sys, os
sys.path.append(os.path.realpath(__file__)[:os.path.realpath(__file__).rfind("/")] + "/")

from dkmonitor.utilities.log_setup import setup_logger
class ConfigurationFilesNotFoundError(Exception):
    def __init__(self, message):
        super(ConfigurationFilesNotFoundError, self).__init__(message)

class ConfigReader():
    """
    ConfigReader Does four things:
        1) Check program settings
        2) Log issues
        3) Set bad settings to defaults
        4) Exports settings in a dictionary
    """

    def __init__(self):
        self.logger = setup_logger("settings_log.log")
        try:
            self.config_root = os.environ["DKM_CONF"]
        except KeyError as err:
            self.logger.critical("No configuration files found, DKM_CONF not set")
            print("ERROR: ***No Configuration files found***")
            raise err

        if not os.path.exists(self.config_root):
            self.logger.critical("No configuration files found, path in DKM_CONF is bad")
            raise ConfigurationFilesNotFoundError("The path specified in DKM_CONF does not exist")
        if os.path.isfile(self.config_root):
            self.logger.critical("No configuration files found, path in DKM_CONF points to a file")
            raise ConfigurationFilesNotFoundError("The path specifed in DKM_CONF points to a file")

        try:
            with open(os.path.dirname(os.path.realpath(__file__)) + '/' + "settings_configurations.json", "r") as jfile:
                self.option_list = json.load(jfile)
        except OSError as err:
            self.logger.critical("Cannot find the settings_configuration.json"
                                 "file to check configurations")
            raise err

        self.config_dict = self.load_configs()

    #Config Parsing Methods###################################################################

    def load_configs(self):
        """Loads config files into a dictionary and returns the dictionary"""

        config_dict = {"task": {}, "general": configparser.ConfigParser()}
        config_dict["general"].read(self.config_root + "/general_settings.cfg")
        task_files = self.read_tasks()
        for task in task_files:
            config_dict["task"][task] = configparser.ConfigParser()
            config_dict["task"][task].read(task)
        return config_dict

    def read_tasks(self):
        """Gets and returns full path to all task files in a list"""

        task_root = self.config_root + "/tasks/"
        try:
            task_files = glob.glob(task_root + "/*.cfg")
        except OSError as err:
            self.logger.critical("No tasks directory found in DKM_CONF")
            raise err

        return task_files

    def verify_configs(self):
        """
        Runs methods to verify all configs
        Returns dict populated with correct settings if settings
        Returns False if there is a critical issue
        """

        good_flag = self.verify_options()
        if good_flag is False:
            self.logger.critical("Program Halting")
            return good_flag

        good_flag = self.test_db_connection()
        if good_flag is not False:
            return self.configs_to_dict()

    def configs_to_dict(self):
        """Converts all config files to a dictionary and returns the dictionary"""

        export_dict = {}

        #General Settigns
        gen_sections = self.config_dict["general"].sections()
        for section in gen_sections:
            export_dict[section] = self.section_to_dict(self.config_dict["general"], section)

        #Task Settings
        export_dict["Scheduled_Tasks"] = {}
        for task, task_config in list(self.config_dict["task"].items()):
            task_sections = task_config.sections()
            export_dict["Scheduled_Tasks"][task] = {}
            for section in task_sections:
                export_dict["Scheduled_Tasks"][task][section] = self.section_to_dict(task_config, section)

        return self.check_set_option_dependencies(export_dict)


    @staticmethod
    def section_to_dict(config, section):
        """Converts section from a config file to dictionary format"""

        add_dict = dict(config.items(section))
        for field in add_dict.keys():
            if add_dict[field].isdigit():
                add_dict[field] = int(add_dict[field])

        return add_dict

    #DB Connection Methods###############################################################

    def test_db_connection(self):
        """Quick Connection check"""

        db_dict = dict(self.config_dict["general"].items("DataBase_Settings"))
        try:
            psycopg2.connect(database=db_dict['database'],
                             user=db_dict['user_name'],
                             password=db_dict['password'],
                             host=db_dict['host'])
        except psycopg2.DatabaseError as db_error:
            self.logger.error(db_error)
            return False
        return True


    #JSON object Verifcation Methods#####################################################

    def check_set_option_dependencies(self, settings_dict):
        """ A function where the settings that are dependent on eachother can be checked and set """

        no_email_flag = False
        if settings_dict["Email_Settings"]["user_postfix"] == "":
            self.logger.warning("user_postfix in Email_Settings has not been set")
            self.logger.warning("Not emailing users")
            no_email_flag = True

        for item in settings_dict["Scheduled_Tasks"].items():
            task = item[1]
            if task["Threshold_Settings"]["disk_use_percent_critical_threshold"] <= task["Threshold_Settings"]["disk_use_percent_warning_threshold"]:
                self.logger.warning("Disk use percent critical threshold must be greater than disk_use_percent_warning_threshold")
                self.logger.warning("Setting to system defualts")
                task["Threshold_Settings"]["disk_use_percent_warning_threshold"] = int(self.find_default("disk_use_percent_warning_threshold"))
                task["Threshold_Settings"]["disk_use_percent_critical_threshold"] = int(self.find_default("disk_use_percent_critical_threshold"))

            if (task["Scan_Settings"]["relocate_old_files"] == "yes") and (task["Scan_Settings"]["delete_old_files"] == "yes"):
                self.logger.warning("Both relocate_old_files and delete_old_files cannnot be set to yes")
                self.logger.warning("Setting both values to 'no'")
                task["Scan_Settings"]["relocate_old_files"] = "no"
                task["Scan_Settings"]["delete_old_files"] = "no"

            if (task["Scan_Settings"]["relocate_old_files"] == "yes") and (task["Scan_Settings"]["file_relocation_path"] == ""):
                self.logger.error("You have set relocate_old_files to yes but did not set file_relocation_path")
                self.logger.warning("Setting relocate_old_files to 'no'")

            if no_email_flag is True:
                task["Email_Settings"]["email_data_alteration_notices"] = "no"
                task["Email_Settings"]["email_usage_warnings"] = "no"

        return settings_dict



    def find_default(self, option_name):
        """Finds the default value of an option from the option json file"""

        for option in self.option_list:
            if option["option_name"] == option_name:
                return option["default_value"]

    def verify_option(self, config, option):
        """Verifies a Single option from settings_configuration.json"""

        good_flag = True

        try:
            otype = option["type"]
            if otype == "bool":
                self.verify_boolean_field(config, option)
            elif otype == "int":
                self.check_log_set_int(config, option)
            elif otype == "path":
                good_flag = self.verify_path_field(config, option)
            elif otype == "str":
                good_flag = self.verify_str_field(config, option)

        except NoSectionError:
            if option["error"] == "critical":
                self.logger.critical("The section %s does not exist", option["section_name"])
                good_flag = False
            else:
                self.logger.error("The section %s does not exist,"
                                  "this could cause problems",
                                  option["section_name"])

        except NoOptionError:
            if option["error"] == "critical":
                self.logger.critical("The option %s in section %s"
                                     "does not exist. Program cannot run",
                                     option["option_name"],
                                     option["section_name"])
                good_flag = False
            else:
                self.logger.warning("Option %s was not found. Setting to default",
                                    option["option_name"])
                self.config_dict["config_type"].set(option["section_name"],
                                                    option["option_name"],
                                                    option["default_value"])

        return good_flag


    def verify_options(self):
        """
        Verifies all options from settings_configuration.json by calling verify_option
        Returns true if settings are good
        Returns False if settings are bad
        """

        good_flag = True
        task_flags = {}
        gen_flags = []
        for option in self.option_list:
            if option["config_type"] == "task":
                task_files = self.read_tasks()
                for task_file in task_files:
                    if task_file not in task_flags.keys():
                        task_flags[task_file] = [self.verify_option(self.config_dict["task"][task_file], option)]
                    else:
                        task_flags[task_file].append(self.verify_option(self.config_dict["task"][task_file], option))
            else:
                gen_flags.append(self.verify_option(self.config_dict["general"], option))

        if False in gen_flags:
            self.logger.critical("Too many issues in general_settings.cfg. Program halting")
            good_flag = False

        for key, flag_list in list(task_flags.items()):
            if False in flag_list:
                del task_flags[key]
                self.logger.error("Too many issues in config file %s. Skipping task.", key)
                good_flag = False

        return good_flag


    #Verification Methods################################################################

    def verify_path_field(self, config, option):
        """
        Verifies that a path field is correct
        Returns false if path is bad
        Returns True if path is goo
        Returns True if path is bad but not critical
        """

        good_flag = True
        path = config.get(option["section_name"], option["option_name"])
        good_flag = self.verify_str_field(config, option)
        if not os.path.exists(path):
            if option["error"] == "warning":
                self.logger.warning("The path field %s in section: %s does not exist",
                                    option["option_name"],
                                    option["section_name"])
                good_flag = True

            elif option["error"] == "critical":
                self.logger.error("The path field %s in section: %s does not exist",
                                  option["option_name"],
                                  option["section_name"])
                good_flag = False

        if option["error"] == "warning":
            return True
        return good_flag

    def verify_str_field(self, config, option):
        """Verifies that a string field has a value"""

        good_flag = True
        string = config.get(option["section_name"], option["option_name"])
        if string == "":
            if option["error"] == "warning":
                self.logger.warning("The field %s in section: %s is not set",
                                    option["option_name"],
                                    option["section_name"])
            if option["error"] == "critical":
                self.logger.error("The field %s in section: %s is not set",
                                  option["option_name"],
                                  option["section_name"])
                self.logger.error("Program aborting")
                good_flag = False
            good_flag = False

        if option["error"] == "warning":
            good_flag = True
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
                                "(yes/no, true/false, on/off, 1/0)",
                                option["option_name"],
                                option["section_name"])
            self.logger.warning("Setting %s flag to: '%s'")
            config.set(option["section_name"], option["option_name"], option["default_value"])

        return good_flag


    def verify_int_field(self, config, option):
        """
        Verifies An integer field
        if no integer is found, return False
        else return the value captured
        """

        int_val = False
        try:
            int_val = config.getint(option["section_name"], option["option_name"])
        except ValueError:
            self.logger.warning("The %s set in %s must be an integer",
                                option["option_name"],
                                option["section_name"])
            self.logger.warning("Setting %s to default value: %s",
                                option["option_name"],
                                option["default_value"])
            config.set(option["section_name"], option["option_name"], option["default_value"])

        return int_val

    def check_log_set_int(self, config, option):
        """
        Deals with integer options
        Checks if integer value is correct based on min and max values in json file
        """

        value = self.verify_int_field(config, option)
        if (option["mininum"] != "") and (option["maximum"] != ""):
            if value not in range(int(option["mininum"]), int(option["maximum"])):
                self.logger.warning("The %s set in %s must be an integer between %s and %s",
                                    option["option_name"],
                                    option["section_name"],
                                    option["mininum"],
                                    option["maximum"])
                self.logger.warning("Setting %s to default value: %s",
                                    option["option_name"],
                                    option["default_value"])
                config.set(option["section_name"], option["option_name"], option["default_value"])

        elif option["mininum"] != "":
            if value < int(option["mininum"]):
                self.logger.warning("%s field in: %s must be an integer bigger than %s",
                                    option["option_name"],
                                    option["section_name"],
                                    option["mininum"])
                self.logger.warning("Setting %s to defualt value: %s",
                                    option["option_name"],
                                    option["default_value"])
                config.set(option["section_name"], option["option_name"], option["default_value"])

        return value


if __name__ == "__main__":
    test = ConfigReader()
    import pprint
    pprint.pprint(test.verify_configs())
    #print(test.verify_configs())
