"""
File containing the SettingsInterface class
This class is used to parse ini files,
check if the settings are correct
and then converts them into a dictionary for monitor_manager
"""

import psycopg2

import sys, os
sys.path.append(os.path.abspath("../.."))

from dkmonitor.utilities.field_lists import FieldLists
from dkmonitor.utilities import log_setup

class SettingsInterface(FieldLists):
    """
    The settings interface class acts as interface between the configparser ini files
    and the monitor manager class
    """

    def __init__(self):
        FieldLists.__init__(self)
        self.logger = log_setup.setup_logger("settings_log.log")

        self.settings = {"Scheduled_Tasks" : {},
                         "DataBase_info" : None,
                         "Email_API" : None,
                         "Thread_Settings": None}

        self.task_config.read(self.task_config_file_name)
        self.gen_config.read(self.gen_config_file_name)


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


    def parse_and_check_all(self):
        """
        parses and configures all sections in all config files
        if there are critical errors the program halts
        returns settings dict if all is good
        """

        flag_list = []
        flag_list.append(self.read_db())
        flag_list.append(self.read_email())
        flag_list.append(self.read_thread())
        flag_list.append(self.read_tasks())

        if True in flag_list:
            self.logger.critical("Too Many configuration issues: Program Halting")
            sys.exit("CRITICAL ERROR: Too Many configuration issues: Program Halting")
        return self.settings

####Field Verification Functions######################
    def verify_boolean_field(self, config, section, flag_name, default):

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

    def check_log_set_range(self, config, section, field_name, value, default, range_min, range_max):
        if value not in range(range_min, range_max):
            self.logger.warning("The %s set in %s must be an integer between %s and %s",
                                field_name,
                                section,
                                range_min,
                                range_max)
            self.logger.warning("Setting %s to default value: %s", field_name, default)
            config.set(section, field_name, default)


    def check_log_set_isgreater(self, config, section, field_name, value, default, min_val):
        if value < min_val:
            self.logger.warning("%s field in: %s must be an integer bigger than %s",
                                field_name,
                                section,
                                min_val)
            self.logger.warning("Setting %s field in: %s "
                                "to defualt value: %s days", field_name, section, default)
            self.task_config.set(section, "last_access_threshold", default)




####DATABASE SETTINGS#############################################################
    def read_db(self):
        """Reads, checks and parses the DataBase_Settings section"""

        bad_flag = self.check_options(self.gen_config,
                                      "DataBase_Settings",
                                      self.db_fields)
        if bad_flag is False:
            bad_flag = self.test_db_connection()
        if bad_flag is False:
            self.verify_db_feilds()
        if bad_flag is False:
            self.settings["DataBase_info"] = self.config_to_dict(self.gen_config,
                                                                 "DataBase_Settings")

        return bad_flag

    def verify_db_feilds(self):
        """Verifies db fields"""

        pdefault = "no"
        pdb = self.verify_boolean_field(self.gen_config, "DataBase_Settings", "purge_database", "no")
        if pdb == 1:
            self.verify_purge_days()

    def verify_purge_days(self):
        """Verifies pure days field. Sets field if incorrect"""

        pdefault = "30"
        pdays = self.verify_int_field(self.gen_config, "DataBase_Settings", "purge_after_day_number", pdefault)
        self.check_log_set_isgreater(self.gen_config, "DataBase_Settings", "purge_after_day_number", pdays, pdefault, 1)


    def test_db_connection(self):
        """Quick Connection check"""

        db_dict = dict(self.gen_config.items("DataBase_Settings"))
        try:
            psycopg2.connect(database=db_dict['database'],
                             user=db_dict['user_name'],
                             password=db_dict['password'],
                             host=db_dict['host'])
        except psycopg2.DatabaseError as db_error:
            self.logger.error(db_error)
            return True
        return False

####THREAD SETTINGS#########################################
    def read_thread(self):
        """Reads, checks and parses the Thread_Settings section"""

        bad_flag = self.check_options(self.gen_config, "Thread_Settings", self.thread_fields)

        if bad_flag is False:
            self.verify_thread_fields()

        if bad_flag is False:
            self.settings["Thread_Settings"] = self.config_to_dict(self.gen_config,
                                                                   "Thread_Settings")

        return bad_flag


    def verify_thread_fields(self):
        """Verifies thread settings fields"""

        tdefault = "no"
        thread_mode = self.verify_boolean_field(self.gen_config, "Thread_Settings", "thread_mode", tdefault)
        if thread_mode == 1:
            self.verify_thread_num()

    def verify_thread_num(self):
        """Verifies the thread num field. sets to 4 threads if incorrect"""

        tdefault = "4"
        thread_num = self.verify_int_field(self.gen_config, "Thread_Settings", "thread_number", tdefault)
        self.check_log_set_isgreater(self.gen_config, "Thread_Settings", "thread_number", thread_num, tdefault, 1)

####EMAIL SETTINGS##########################################
    def read_email(self):
        """Reads, checks and parses the Email_Settings section"""

        bad_flag = self.check_options(self.gen_config, "Email_Settings", self.email_fields)

        if bad_flag is False:
            self.verify_email_fields()

        if bad_flag is False:
            self.settings["Email_API"] = self.config_to_dict(self.gen_config, "Email_Settings")

        return bad_flag

    #TODO set all email flags to off if not list of postfix
    def verify_email_fields(self):
        """Checks Email_Settings fields"""

        pflag = True
        if self.gen_config.get("Email_Settings", "user_postfix") == "":
            self.logger.warning("User_postfix in Email_Settings is not set")
            pflag = False

        list_path = self.gen_config.get("Email_Settings", "email_list")
        if list_path == "":
            if pflag is False:
                self.set_task_emails()
                self.logger.warning("Emails will not be sent")

        else:
            if not os.path.exists(list_path):
                self.logger.warning("email_list path set in Email_Settings does not exist")
                if pflag is False:
                    self.set_task_emails()
                    self.logger.warning("Emails will not be sent")

    def set_task_emails(self):
        """Sets all task's email flag to no"""

        sections = self.task_config.sections()
        for section in sections:
            self.task_config.set(section, "email_users", "no")


####TASK SETTINGS###########################################
    def read_tasks(self):
        """
        Reads and verifies the sections in the tasks configparser file
        If all input is correct it will add them to the settings dictionary
        """

        flag_list = []
        unchecked_sections = self.task_config.sections()
        for section in unchecked_sections:
            bad_flag = self.check_options(self.task_config, section, self.task_fields)

            if bad_flag is False:
                bad_flag = self.verify_task_fields(section)

            if bad_flag is False:
                self.settings["Scheduled_Tasks"][section] = self.config_to_dict(self.task_config,
                                                                                section)
            else:
                self.logger.warning("Task %f will be skipped", section)

            flag_list.append(bad_flag)

        if False in flag_list:
            return False
        else:
            return True

    def verify_task_fields(self, section):
        """Verifies the settings in a task field"""

        bad_flag = False #Set to true if there is a critcal error

        system = self.task_config.get(section, "system_name")
        if system == "":
            self.logger.error("System field is not set in: %s", section)
            bad_flag = True

    ####Directory_Path####
        sdir = self.task_config.get(section, "directory_path")
        if sdir == "":
            self.logger.error("Directory Path field is not set in: %s", section)
            bad_flag = True
        elif not os.path.exists(sdir):
            self.logger.error("Directory Path field set in: %s does not exist", section)
            bad_flag = True

        delete_flag = self.verify_boolean_field(self.task_config, section, "delete_old_files", "no")
        if delete_flag == 1:
            self.verify_thresholds(section)
            self.task_config.set(section, "delete_old_files", "yes")

    ####Relocate flag####
        relocate_flag = self.verify_boolean_field(self.task_config, section, "relocate_old_files", "no")
        if relocate_flag == 1:
            self.verify_relocate_fields(section)

        #TODO set relocate_flag to yes if both delete and relocate_flag are yes

        if (delete_flag == 1) and (relocate_flag == 1):
            self.logger.warning("delete_old_files and relocate_old_files are both set to true."
                                "Only one can be set to yes at a time")
            self.logger.warning("Setting both delete_old_files and relocate_old_files to 'no'")
            self.task_config.set(section, "delete_old_files", "no")
            self.task_config.set(section, "relocate_old_files", "no")

        if delete_flag == 1:
            self.verify_thresholds(section)
        elif relocate_flag == 1:
            self.verify_relocate_fields(section)


        return bad_flag


    def verify_relocate_fields(self, section):
        """Verifies the fields related to file relocation"""

        set_flag = False #Set to true if a default value needs to be set
    ####RELOCATE PATH####
        relocate_path = self.task_config.get(section, "file_relocation_path")
        if relocate_path == "":
            self.logger.warning("The Relocation file path Field in: %s is not set", section)
            set_flag = True
        elif not os.path.exists(relocate_path):
            self.logger.warning("The Relocation file path set in %s does not exist", section)
            set_flag = True

        if set_flag is True:
            self.logger.warning("Not Moving old files")
            self.task_config.set(section, "relocate_old_files", "no")
            set_flag = False
        else:
            self.verify_thresholds(section)

    def verify_thresholds(self, section):
    ####Disk_Use_Percent#####
        wdefault = "70"
        warning_disk_use = self.verify_int_field(self.task_config,
                                                 section,
                                                 "disk_use_percent_warning_threshold",
                                                 wdefault)
        self.check_log_set_range(self.task_config,
                                 section,
                                 "disk_use_percent_warning_threshold",
                                 warning_disk_use,
                                 wdefault,
                                 1,
                                 100)

        cdefault = "85"
        critical_disk_use = self.verify_int_field(self.task_config,
                                                  section,
                                                  "disk_use_percent_critical_threshold",
                                                  cdefault)
        self.check_log_set_range(self.task_config,
                                 section,
                                 "disk_use_percent_critical_threshold",
                                 critical_disk_use,
                                 cdefault,
                                 1,
                                 100)

        #Check for conflicting threshold values
        if warning_disk_use > critical_disk_use:
            self.logger.warning("disk_use_percent_critical_threshold must be greater than"
                                "disk_use_percent_warning_threshold")
            self.logger.warning("Setting disk_use_percent_warning_threshold to %s", wdefault)
            self.logger.warning("Setting disk_use_percent_critical_threshold to %s", cdefault)

    ####LAST ACCESS####
        adefault = "7"
        access_val = self.verify_int_field(self.task_config, section, "last_access_threshold", adefault)
        self.check_log_set_isgreater(self.task_config, section, "last_access_threshold", access_val, adefault, 1)

    ####EMAIL####
    def verify_email_options(self, section):
        """Verifies the bad_flag_percent field if email users is set to true"""

        email_flag = self.verify_boolean_field(self.task_config, section, "email_users", "no")
        if email_flag == 1:
            self.verify_email_options(section)

        bdefault = "25"
        bad_percent = self.verify_int_field(self.task_config, section, "bad_flag_percent", bdefault)
        self.check_log_set_range(self.task_config, section, "bad_flag_percent", bad_percent, bdefault, 1, 100)



if __name__ == '__main__':
    Setobj = SettingsInterface()
    sett = Setobj.parse_and_check_all()
    print(sett)

