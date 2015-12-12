"""
Setup script
"""
from setuptools import setup, find_packages
from setuptools.command.install import install

import shutil, os

def long_description():
    """Opens Readme for long description"""
    with open("README.rst", "r") as readme:
        return readme.readlines()

class BuildDkm(install):
    """Custom install class"""

    def run(self):
        install.do_egg_install(self) #installs required packages

        root_flag = False
        home_flag = False
        try:
            os.makedirs("/etc/dkmonitor")
            os.makedirs("/var/log/dkmonitor")
            shutil.copyfile(os.path.realpath("./dkmonitor/conf/settings.cfg"), "/etc/dkmonitor")
            root_flag = True
        except OSError as err:
            if err.errno == 13: #Permission error
                try:
                    os.makedirs(os.path.expanduser("~/.dkmonitor/log"))
                    shutil.copyfile(os.path.realpath("./dkmonitor/conf/settings.cfg"),
                                    os.path.expanduser("~/.dkmonitor"))
                    home_flag = True
                except OSError as err2:
                    if err2.errno == 17: #File not exsists error
                        print("Warning: ~/.dkmonitor already exists")
                    else:
                        raise err2
            if err.errno == 17: #File exsists error
                print("Warning /etc/dkmonitor or /var/log/dkmonitor already exsist")


        if root_flag is True:
            print("""

            Your settings file is located at /etc/dkmonitor/settings.cfg
            Your log files will be saved at /var/log/dkmonitor
            """)

        if home_flag is True:
            print("""

            Your settings file is located at ~/.dkmonitor/conf/settings.cfg
            Your log files will be saved at ~/.dkmonitor/log/
            """)


setup(name="dkmonitor",
      version="1.0.0",
      description="Monitors specified disks or directories for user and general stats",
      license="MIT",
      author="William Patterson",
      packages=find_packages(),
      package_data={'dkmonitor.config': ['*.cfg'],
                    'dkmonitor.emailer.messages': ['*.txt']},
      install_requires=["sqlalchemy", "psycopg2", "termcolor"],
      long_description=long_description(),
      cmdclass={'install': BuildDkm},
      entry_points={"console_scripts": ["dkmonitor=dkmonitor.__main__:main"],})
