"""
Setup script
"""
from distutils.errors import DistutilsOptionError
from setuptools import setup, find_packages
from setuptools.command.install import install

import sys
import os
sys.path.append(os.path.abspath("."))

from dkmonitor.config.settings_file_generator import generate_config_files

long_description = "open file here"

class BuildDkm(install):
    install.user_options.append(("log-path=", None, "Specify the directory to store log files in"))
    install.user_options.append(("conf-path=", None, "Specify the directory where config files are stored"))
    install.user_options.append(("root-path=", None, "Specify the directory with both config and log fils are stored"))

    def initialize_options(self):
        super().initialize_options()
        self.log_path = None #"/var/log/dkmonitor"
        self.conf_path = None #"/etc/dkmonitor"
        self.root_path = None

    def finalize_options(self):
        super().finalize_options()

        if self.root_path is None:
            if (self.log_path is None):
                self.log_path = os.path.abspath(os.path.expanduser("~/.dkmonitor/log/"))
            else:
                self.log_path = os.path.abspath(os.path.expanduser(self.log_path))
            if self.conf_path is None:
                self.conf_path = os.path.abspath(os.path.expanduser("~/.dkmonitor/conf/"))
            else:
                self.conf_path = os.path.abspath(os.path.expanduser(self.conf_path))
        else:
            if self.log_path is not None:
                raise DistutilsOptionError("Cannot combine log-path and root-path options")
            if self.conf_path is not None:
                raise DistutilsOptionError("Cannot combine conf-path and root-path options")

            self.root_path = os.path.abspath(os.path.expanduser(self.root_path) + "/dkmonitor/")
            self.log_path = self.root_path + "/log/"
            self.conf_path = self.root_path + "/conf/"

    def run(self):
        try:
            print("creating config and log directories")
            if self.root_path is None:
                os.makedirs(self.log_path)
                os.makedirs(self.conf_path + "/tasks/")
            else:
                os.makedirs((self.root_path)
                os.makedirs(self.conf_path + "/tasks/")
                os.mkdir(self.log_path)
        except OSError:
            print("warning: conf and log paths exist")


        generate_config_files(self.conf_path, "dkmonitor/config/settings_configurations.json")

        #install.run(self)
        install.do_egg_install(self)

        print("""

              Add these lines to your bashrc file:
              export DKM_LOG={log}
              export DKM_CONF={conf}
              """.format(log=self.log_path, conf=self.conf_path))


setup(name="dkmonitor",
      version="1.0.0",
      description="Monitors specified disks or directories for user and general stats",
      license="MIT",
      author="William Patterson",
      packages=find_packages(),
      package_data={'dkmonitor.config': ['*.json'],
                    'dkmonitor.emailer.messages': ['*.txt'],
                    'dkmonitor.utilities': ['*.sql']},
      install_requires=["psycopg2", "termcolor"],
      long_description="long_description",
      cmdclass={'install': BuildDkm},
      entry_points={"console_scripts": ["dkmonitor=dkmonitor.monitor_manager:main",
                                        "create_database=dkmonitor.utilities.create_db:main",
                                        "dkviewer=dkmonitor.admin_interface.main",
                                        "dktask=dkmonitor.config.settings_file_generator.main"],})
