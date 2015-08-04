"""
Setup script
"""
from setuptools import setup, find_packages
from setuptools.command.install import install


import sys
import os
sys.path.append(os.getcwd() + "/..")

import dkmonitor.configurator_settings_generator as config_gen

long_description = "open file here"

class BuildDkm(install):
    """Customized install class"""
    def run(self):
        root_path = os.path.expanduser("~/.dkmonitor/")
        log_path = root_path + "log"
        config_path = root_path + "conifg"
        if not os.path.exists(root_path):
            os.mkdir(root_path)
            os.mkdir(log_path)
            os.mkdir(config_path)

        conf_gen = config_gen.ConfigGenerator()
        conf_gen.generate_defaults()

        install.run(self)

setup(name="dbtracker",
      version="1.0.0",
      description="Monitors specified disks or directories for user and general stats",
      license="MIT",
      author="William Patterson",
      packages=find_packages(),
      install_requires=["psycopg2"],
      long_description=long_description,
      cmdclass={'install': BuildDkm},
      entry_points={"console_scripts": ["dkmonitor=dkmonitor.monitor_manager:main"],}) #Could use some more thought
