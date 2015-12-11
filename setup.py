"""
Setup script
"""
from distutils.errors import DistutilsOptionError
from setuptools import setup, find_packages
from setuptools.command.install import install

import shutil
import os, sys

long_description = "open file here"

class BuildDkm(install):
    """Custom install class"""
    install.user_options.append(("log-path=",
                                 None,
                                 "Specify the directory to store log files in"))
    install.user_options.append(("conf-path=",
                                 None,
                                 "Specify the directory where config files are stored"))
    install.user_options.append(("root-path=",
                                 None,
                                 "Specify the directory with both config and log fils are stored"))

    def initialize_options(self):
        super().initialize_options()
        self.log_path = None #"/var/log/dkmonitor"
        self.conf_path = None #"/etc/dkmonitor"
        self.root_path = None

    def finalize_options(self):
        super().finalize_options()

        if ((self.log_path is not None) or (self.conf_path is not None)) \
           and (self.root_path is not None):
            raise DistutilsOptionError("Cannot combine log-path/conf-path and root-path options")

    def run(self):

        set_path_flag = False
        try:
            print("creating config and log directories")
            if self.root_path is None:
                os.makedirs(self.log_path)
                os.makedirs(self.conf_path)
                shutil.copyfile("./dkmonitor/config/settings.cfg", self.conf_path)
            else:
                os.makedirs(self.root_path)
                os.makedirs(self.conf_path)
                shutil.copyfile("./dkmonitor/config/settings.cfg", self.conf_path)
                os.mkdir(self.log_path)
            set_path_flag = True
        except AttributeError: #If paths are None
            try:
                os.makedirs("/etc/dkmonitor/")
                os.makedirs("/var/log/dkmonitor/")
                shutil.copyfile("./dkmonitor/config/settings.cfg", "/etc/dkmonitor/")
            except OSError as err:
                if err.errno == 13: #Permission error
                    try:
                        os.makedirs("~/.dkmonitor/conf/")
                        os.makedirs("~/.dkmonitor/log")
                        shutil.copyfile("./dkmonitor/config/settings.cfg", "~/.dkmonitor/conf/")
                    except OSError as oserr:
                        if oserr.errno == 17: #File exists
                            print("Warning: ~/.dkmonitor already exists")
                elif err.errno == 17: #File exists
                    print("Warning: /etc/dkmonitor and /var/log/dkmonitor already exist")
        except OSError as err:
            if err.errno == 13: #Permission error
                raise err
            elif err.errno == 17: #File exists
                print("warning: conf and log paths already exist")

        install.do_egg_install(self)

        if set_path_flag is True:
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
      package_data={'dkmonitor.config': ['*.cfg'],
                    'dkmonitor.emailer.messages': ['*.txt']},
      install_requires=["sqlalchemy", "psycopg2", "termcolor"],
      long_description="long_description",
      cmdclass={'install': BuildDkm},
      entry_points={"console_scripts": ["dkmonitor=dkmonitor.__main__:main"],})
