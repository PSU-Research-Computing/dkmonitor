import configparser
import os
import psycopg2

import field_lists

class SettingsInterface(field_lists.FieldLists):
    """
    The settings interface class acts as interface between the configparser ini files 
    and the monitor manager class
    """

    def __init__(self):
        field_lists.FieldLists.__init__(self)

        self.settings = {"Scheduled_Tasks" : [],
                         "DataBase_info" : None,
                         "Email_API" : None,
                         "Thread_Settings": None}

        self.task_config_file_name = "../tasks.cfg"
        self.gen_config_file_name = "../general.cfg"

        self.task_config = configparser.ConfigParser()
        self.gen_config = configparser.ConfigParser()

        self.task_config.read(self.task_config_file_name)
        self.gen_config.read(self.gen_config_file_name)

    def read_tasks(self):
        """
        Reads and verifies the sections in the tasks configparser file
        If all input is correct it will add them to the settings dictionary
        """

        unchecked_sections = self.task_config.sections()
        for section in unchecked_sections:
            bad_flag = self.check_task_fields(section)
            if bad_flag == False:
                add_dict = dict(self.task_config.items(section))
                #TODO figure out how to convert ints to strings before adding to the settings dict
                self.settings["Scheduled_Tasks"].append()

    def check_task_fields(self, section):
        """
        Checks a task for all the correct fields
        If fields are correct, then it verifies the settings
        """

        bad_flag = False
        for field in self.task_fields:
            if not self.task_config.has_option(section, field):
                bad_flag = True
                print("ERROR: Missing Field: {f}".format(f=field))

        if bad_flag == False:
            bad_flag = self.verify_task_fields(section)

        return bad_flag


    #TODO Set default settings if settings are incorrect
    def verify_task_fields(self, section):
        """Verifies the settings in a task field"""

        bad_flag = False #Set to true if there is a critcal error
        set_flag = False #Set to true if a default value needs to be set

        system = self.task_config.get(section, "system_name")
        if system == "":
            print("WARNING: System field is not set in: {s}".format(s=section))

        sdir = self.task_config.get(section, "directory_path")
        if sdir == "":
            print("CRICICAL ERROR: Directory Path field is not set in: {s}".format(s=section))
            bad_flag = True
        elif not os.path.exists(sdir):
            print("CRICICAL ERROR: Directory Path field set in: {s} does not exist".format(s=section))
            bad_flag = True

        relocate_path = self.task_config.get(section, "file_relocation_path")
        if (relocate_path != "") and (not os.path.exists(relocate_path)):
            print("ERROR: The Relocation file path Field set in: {s} does not exist".format(s=section))
            print("Not Moving files")

        try:
            dupt = self.task_config.getint(section, "disk_use_percent_threshold")
            if dupt > 100 or dupt < 1:
                print("ERROR: The Disk use percent threshold set in {s} must be an integer between 1 and 100".format(s=section))
                set_flag = True
        except ValueError:
            print("ERROR: Disk Use percent threshold set in {s} must me set to an integer".format(s=section))
            set_flag = True

        if set_flag == True:
            print("Setting Disk use percent threshold to default value: 75%")
            self.task_config.set(section, "disk_use_percent_threshold", "80")
            set_flag = False

        try:
            email_bool = self.task_config.getboolean(section, "email_users")
        except ValueError:
            print("ERROR: The Email users flag set in: {s} must be a boolean value (yes/no, true/false, on/off, 1/0".format(s=section))

        try:
            lat = self.task_config.getint(section, "last_access_threshold")
            if lat < 1:
                print("ERROR: Last access threshold field in: {s} must be an integer bigger than 1".format(s=section))
        except ValueError:
            print("ERROR: The Last access threshold field in: {s} must be an integer bigger than 1".format(s=section))

        try:
            bfp = self.task_config.getint(section, "bad_flag_percent")
            if bfp > 100 or bfp < 1:
                print("ERROR: The Bad flag percent field set in {s} must be an integer between 1 and 100".format(s=section))
        except ValueError:
            print("ERROR: The Bad flag percent field set in {s} must me set to an integer".format(s=section))

        return bad_flag


    def read_db(self):
        bad_flag = False
        for field in self.db_fields:
            if not self.gen_config.has_option("DataBase_Settings", field):
                bad_flag = True
                print("ERROR: Missing Field: {f}".format(f=field))

        if bad_flag == False:
            db_dict = dict(self.gen_config.items("DataBase_Settings"))
            bad_flag = self.test_db_connection(db_dict["database"],
                                               db_dict["user_name"],
                                               db_dict["password"],
                                               db_dict["host"])

            if bad_flag == False:
                try:
                    purge_days = self.gen_config.getint("DataBase_Settings", "purge_after_day_number")
                    if purge_days < 1:
                        print("ERROR: Purge after day number flag in DataBase_Settings must be an integer greater than 1")
                except ValueError:
                    print("ERROR: Purge after day number flag in DataBase_Settings must be an integer greater than 1")

        if bad_flag == False:
            self.settings["DataBase_info"] = dict(self.gen_config.items("DataBase_Settings"))

    def test_db_connection(self, db_name, user, password, host):
        """Quick Connection check"""

        try:
            psycopg2.connect(database=db_name,
                             user=user,
                             password=password,
                             host=host)
        except psycopg2.DatabaseError:# as db_error:
            return True
        return False

    def read_thread(self):

        bad_flag = False
        for field in self.db_fields:
            if not self.gen_config.has_option("Thread_Settings", field):
                bad_flag = True
                print("ERROR: Missing Field: {f}".format(f=field))

        if bad_flag == False:
            bad_flag = self.verify_thread_fields()

    def verify_thread_fields(self):
        bad_flag = False
        try:
            thread_mode = self.gen_config.getboolean("Thread_Settings", "thread_mode")
        except ValueError:
            print("ERROR: The thread mode flag must be a boolean value (yes/no, true/false, on/off, 1/0")

        try:
            thread_num = self.gen_config.getint("Thread_Settings", "thread_number")
            if thread_num < 1:
                print("ERROR: The Thread Number field must be an integer greater 0")
        except ValueError:
            print("ERROR: The Thread Number field must be an integer greater 0")






