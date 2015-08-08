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

    def generate_defaults(self, path_to_config):

        task_config_file_path = path_to_config + "/tasks/task_example.cfg"
        gen_config_file_path = path_to_config + "general_settings.cfg"

        self.build_config_file(self.task_config, self.task_fields)
        self.build_config_file(self.gen_config, self.general_fields)

        with open(task_config_file_path, 'w') as tconfig:
            self.task_config.write(tconfig)

        with open(gen_config_file_path, 'w') as gconfig:
            self.gen_config.write(gconfig)

if __name__ == "__main__":
    ConfGen = ConfigGenerator()
    ConfGen.generate_defaults()

