import sys, os
sys.path.append(os.path.abspath("../.."))

from dkmonitor.utilities.field_lists import FieldLists
from dkmonitor.utilities import log_setup
from configparser import NoOptionError
from configparser import NoSectionError

class ConfigChecker():
    def __init__(self):
        self.logger = log_setup.setup_logger("settings_log.log")

    def verify_path_field(self, config, option):
        good_flag = True
        path = config.get(option["section_name"], option["option_name"])
        if path == "":
            self.logger.error("The path field %s in section: %s is not set", option["option_name"], option["section_name"])
            good_flag = False
        elif not os.path.exists(path):
            if option["error"] == "warning":
            self.logger.error("The path field %s in section: %s does not exist", option["option_name"], option["section_name"])
            good_flag = False

        if option["error"] == "warning":
            return True
        return good_flag

    def verify_str_field(self, config, option):
        good_flag = True
        string = config.get(option["section_name"], option["option_name"])
        if string == "":
            self.logger.error("The string field %s in section %s was not set", option["option_name"], option["section_name"])
            self.logger.error("Program aborting")
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


    """
    def check_log_set_isgreater(self, config, section, field_name, default, min_val):
        value = self.verify_int_field(config, section, field_name, default)
        if value < min_val:
            self.logger.warning("%s field in: %s must be an integer bigger than %s",
                                field_name,
                                section,
                                min_val)
            self.logger.warning("Setting %s field in: %s "
                                "to defualt value: %s days", field_name, section, default)
            config.set(section, field_name, default)
    """


    def check_options(self, config, section, feild_list):
        """Checks if all fields are present in a given section"""

        bad_flag = False
        for field in feild_list:
            if not config.has_option(section, field):
                bad_flag = True
                self.logger.error("Missing Field: %f in %f", field, section)

        return bad_flag


    def config_to_dict(self, config, section):
        """Converts parsed config file to dictionary format"""

        add_dict = dict(config.items(section))
        for field in add_dict.keys():
            if add_dict[field].isdigit():
                add_dict[field] = int(add_dict[field])

        return add_dict

    def check_option_exists(self, config, section, option):
        bad_flag = True
        if not config.has_option(section, option["option_name"]):
            bad_flag = False
            if option["error"] == "critical":
                self.logger.error("Missing Field: %s in %f", option["option_name"], section)
            else:
                self.logger.warning("Missing Field: %s in %f", option["option_name"], section)

        return bad_flag

