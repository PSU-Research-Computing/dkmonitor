import sys, os
sys.path.append(os.path.abspath("../.."))

from dkmonitor.utilities.field_lists import FieldLists
from dkmonitor.utilities import log_setup

class ConfigChecker():
    def __init__(self):
        self.logger = log_setup.setup_logger("settings_log.log")

    def verify_path_field(self, config, section, field):
        bad_flag = False
        path = config.get(section, field)
        if path == "":
            self.logger.error("The path field %s in section: %s is not set", field, section)
            bad_flag = True
        elif not os.path.exists(path):
            self.logger.error("The path field %s in section: %s does not exist", field, section)
            bad_flag = True

        return bad_flag

    def verify_boolean_field(self, config, section, flag_name, default):
        """
        Verifies a boolean field
        If input in field is in the incorrect format:
        the field is set to default
        """

        bool_val = -1
        try:
            bool_val = config.getboolean(section, flag_name)
            if bool_val is True:
                config.set(section, flag_name, "yes")

        except ValueError:
            self.logger.warning("The %s flag set in: %s must be a boolean value "
                                "(yes/no, true/false, on/off, 1/0)", flag_name, section)
            self.logger.warning("Setting %s flag to: '%s'")
            config.set(section, flag_name, default)

        return int(bool_val)


    def verify_int_field(self, config, section, field_name, default):
        return_val = False
        try:
            return_val = config.getint(section, field_name)
        except ValueError:
            self.logger.warning("The %s set in %s must be an integer", field_name, section)
            self.logger.warning("Setting %s to default value: %s", field_name, default)
            config.set(section, field_name, default)

        return return_val

    def check_log_set_range(self, config, section, field_name, default, range_min, range_max):
        value = self.verify_int_field(config, section, field_name, default)
        if value not in range(range_min, range_max):
            self.logger.warning("The %s set in %s must be an integer between %s and %s",
                                field_name,
                                section,
                                range_min,
                                range_max)
            self.logger.warning("Setting %s to default value: %s", field_name, default)
            config.set(section, field_name, default)


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
