"""
Setup script
"""
from setuptools import setup, find_packages
from setuptools.command.install import install

import shutil, os, errno

def long_description():
    """Opens Readme for long description"""
    with open("README.rst", "r") as readme:
        return readme.readlines()

"""
class BuildDkm(install):

    def run(self):
        root_flag = False
        home_flag = False
        try:
            os.makedirs("/etc/dkmonitor")
            os.makedirs("/var/log/dkmonitor")
            shutil.copyfile(os.path.realpath("./dkmonitor/config/settings.cfg"), "/etc/dkmonitor")
            root_flag = True
        except OSError as err:
            if err.errno == errno.EACCES: #Permission error
                try:
                    os.makedirs(os.path.expanduser("~/.dkmonitor/log"))
                    shutil.copyfile(os.path.realpath("./dkmonitor/config/settings.cfg"),
                                    os.path.expanduser("~/.dkmonitor"))
                    home_flag = True
                except OSError as err2:
                    if err2.errno == errno.EEXIST: #File exsists error
                        print("Warning: ~/.dkmonitor already exists")
                    else:
                        raise err2
            if err.errno == errno.EEXIST: #File exsists error
                print("Warning /etc/dkmonitor or /var/log/dkmonitor already exsist")


        if root_flag is True:
            pass

        if home_flag is True:
            pass
"""

setup(name="dkmonitor",
      version="1.0.0",
      description="Monitors disks and directories for user and general stats",
      license="MIT",
      author="William Patterson",
      packages=find_packages(),
      package_data={'dkmonitor.config': ['*.cfg'],
                    'dkmonitor.emailer.messages': ['*.txt']},
      install_requires=["sqlalchemy", "termcolor"])
      #long_description=long_description())

#entry_points={"console_scripts": ["dkmonitor = dkmonitor.__main__:main",],})
#cmdclass={'install': BuildDkm},
