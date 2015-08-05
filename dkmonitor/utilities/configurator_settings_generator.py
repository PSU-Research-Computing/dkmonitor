
from field_lists import FieldLists

class ConfigGenerator(field_lists.FieldLists):
    """
    ConfigGenerator Offers various functions to create and add to custom config files
    for dkmonitor
    """

    def __init__(self):
        field_lists.FieldLists.__init__(self)

    def add_task_section(self, task_name):
        """Adds a task section to the task_config configuration object"""

        self.task_config.add_section(task_name)
        for field in self.task_fields:
            self.task_config.set(task_name, field, "")

    def build_general_config(self):
        """Builds the general config file with all variables set to nothing"""

        #Database settings
        self.gen_config.add_section("DataBase_Settings")
        for field in self.db_fields:
            self.gen_config.set("DataBase_Settings", field, "")

        #Email Settings
        self.gen_config.add_section("Email_Settings")
        for field in self.email_fields:
            self.gen_config.set("Email_Settings", field, "")

        #Threading Settings
        self.gen_config.add_section("Thread_Settings")
        for field in self.thread_fields:
            self.gen_config.set("Thread_Settings", field, "")

    def generate_defaults(self):
        self.add_task_section("Task_Name")
        with open(self.task_config_file_name, 'w') as tconfig:
            self.task_config.write(tconfig)

        self.build_general_config()
        with open(self.gen_config_file_name, 'w') as gconfig:
            self.gen_config.write(gconfig)

if __name__ == "__main__":
    ConfGen = ConfigGenerator()
    ConfGen.generate_defaults()

