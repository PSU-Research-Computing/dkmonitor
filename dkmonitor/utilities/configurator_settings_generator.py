import sys, os
sys.path.append(os.path.abspath("../.."))

from dkmonitor.utilities.field_lists import FieldLists

class ConfigGenerator(FieldLists):
    """
    ConfigGenerator Offers various functions to create and add to custom config files
    for dkmonitor
    """

    def __init__(self):
        FieldLists.__init__(self)

    def build_config_file(self, config, config_fields):
        """Adds a task section to the task_config configuration object"""

        for section, fields in config_fields.items():
            config.add_section(section)
            for field in fields:
                config.set(section, field, "")

    def generate_defaults(self):
        try:
            os.makedirs(os.path.expanduser("~") + "/.dkmonitor/config/tasks")
        except OSError:
            pass

        self.build_config_file(self.task_config, self.task_fields)
        with open(self.task_config_file_name, 'w') as tconfig:
            self.task_config.write(tconfig)

        self.build_config_file(self.gen_config, self.general_fields)
        with open(self.gen_config_file_name, 'w') as gconfig:
            self.gen_config.write(gconfig)

if __name__ == "__main__":
    ConfGen = ConfigGenerator()
    ConfGen.generate_defaults()

