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

        try:
            purge_bool = self.gen_config.getboolean("DataBase_Settings", "purge_database")
            if purge_bool == True:
                self.verify_purge_days()
                self.gen_config.set("DataBase_Settings", "purge_database", "yes")
        except ValueError:
            self.logger.warning("The purge_database flag must be a"
                                "boolean value (yes/no, true/false, on/off, 1/0")
            self.logger.warning("Setting purge_database flag to: 'no'")

            self.gen_config.set("DataBase_Settings", "purge_database", "no")

    def verify_purge_days(self):
        """Verifies pure days field. Sets field if incorrect"""

        set_flag = False
        try:
            purge_days = self.gen_config.getint("DataBase_Settings", "purge_after_day_number")
            if purge_days < 1:
                self.logger.warning("Purge after day number flag in "
                                    "DataBase_Settings must be an integer greater than 1")

                set_flag = True

        except ValueError:
            self.logger.warning("Purge after day number flag in "
                                "DataBase_Settings must be an integer greater than 1")
            set_flag = True

        if set_flag == True:
            self.logger.warning("The purge_after_day_number field is set to defualt value: 30")
            self.gen_config.set("DataBase_Settings", "purge_after_day_number", "30")


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

        set_flag = False
        try:
            thread_mode = self.gen_config.getboolean("Thread_Settings", "thread_mode")
            if thread_mode is True:
                self.verify_thread_num()
                self.gen_config.set("Thread_Settings", "thread_mode", "yes")
        except ValueError:
            self.logger.warning("The thread mode flag must be a "
                                "boolean value (yes/no, true/false, on/off, 1/0)")
            set_flag = True

        if set_flag is True:
            self.logger.warning("The thread mode flag will be set to default value: 'no'")
            self.gen_config.set("Thread_Settings", "thread_mode", "no")

    def verify_thread_num(self):
        """Verifies the thread num field. sets to 4 threads if incorrect"""

        set_flag = False
        try:
            thread_num = self.gen_config.getint("Thread_Settings", "thread_number")
            if thread_num < 1:
                self.logger.warning("The Thread Number field must be an integer greater 0")
                set_flag = True
        except ValueError:
            self.logger.warning("The Thread Number field must be an integer greater 0")
            set_flag = True

        if set_flag is True:
            self.logger.warning("The thread_num field will be set to defualt value: 4")


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

    ####Relocate flag####
        try:
            r_bool = self.task_config.getboolean(section, "relocate_old_files")
            if r_bool is True:
                self.verify_relocate_fields(section)
                self.task_config.set(section, "relocate_old_files", "yes")
        except ValueError:

            self.logger.warning("The relocate_old_files flag set in: %s must be a boolean value "
                                "(yes/no, true/false, on/off, 1/0)", section)
            self.logger.warning("Setting relocate_old_files flag to: 'no'")
            self.task_config.set(section, "relocate_old_files", "no")

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

    ####Disk_Use_Percent#####
        try:
            dupt = self.task_config.getint(section, "disk_use_percent_threshold")
            if dupt > 100 or dupt < 1:
                self.logger.warning("The Disk use percent threshold set in %s "
                                    "must be an integer between 1 and 100", section)
                set_flag = True

        except ValueError:
            self.logger.warning("Disk Use percent threshold set in %s "
                                "must me set to an integer", section)
            set_flag = True

        if set_flag is True:
            self.logger.warning("Setting Disk use percent threshold to default value: 75 percent")
            self.task_config.set(section, "disk_use_percent_threshold", "75")
            set_flag = False

    ####LAST ACCESS####
        try:
            lat = self.task_config.getint(section, "last_access_threshold")
            if lat < 1:
                self.logger.warning("Last access threshold field in: %s "
                                    "must be an integer bigger than 1", section)
                set_flag = True
        except ValueError:
            self.logger.warning("The Last access threshold field in: %s "
                                "must be an integer bigger than 1", section)
            set_flag = True

        if set_flag is True:
            self.logger.warning("Setting last_access_threshold field in: %s "
                                "to defualt value: 7 days", section)
            self.task_config.set(section, "last_access_threshold", "7")

    ####EMAIL####
        try:
            email_bool = self.task_config.getboolean(section, "email_users")
            if email_bool == True:
                self.task_config.set(section, "email_users", "yes")
                self.verify_email_options(section)

        except ValueError:
            self.logger.warning("The Email users flag set in: %s must be a boolean"
                                " value (yes/no, true/false, on/off, 1/0)", section)
            set_flag = True

        if set_flag is True:
            self.logger.warning("Setting Email users flag set in %s to 'no'", section)
            self.task_config.set(section, "email_users", "no")
            set_flag = False


    def verify_email_options(self, section):
        """Verifies the bad_flag_percent field if email users is set to true"""

        set_flag = False
        try:
            bdays = self.task_config.getint(section, "days_between_runs")
            if bdays < 0:
                self.logger.warning("The days_between_runs field set in %s "
                                    "must be an integer greater than 0", section)
                set_flag = True
        except ValueError:
            self.logger.warning("The days_between_runs field set in %s "
                                "must me set to an integer", section)
            set_flag = True

        if set_flag is True:
            self.logger.warning("Setting days_between_runs field in %s "
                                "to defualt value: 1", section)
            self.task_config.set(section, "days_between_runs", "1")


        set_flag = False
        try:
            bfp = self.task_config.getint(section, "bad_flag_percent")
            if bfp > 100 or bfp < 1:
                self.logger.warning("The Bad flag percent field set in %s "
                                    "must be an integer between 1 and 100", section)
                set_flag = True
        except ValueError:
            self.logger.warning("ERROR: The Bad flag percent field set in %s "
                                "must me set to an integer", section)
            set_flag = True

        if set_flag is True:
            self.logger.warning("Setting bad_flag_percent field in %s "
                                "to defualt value: 25 Percent", section)
            self.task_config.set(section, "bad_flag_percent", "25")




if __name__ == '__main__':
    Setobj = SettingsInterface()
    sett = Setobj.parse_and_check_all()
    print(sett)

