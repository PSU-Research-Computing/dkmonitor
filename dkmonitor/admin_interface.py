"""
Admin interface is a Command Line interface for Administrators that want to view user and system information
"""

import termcolor
import argparse

import sys, os
sys.path.append(os.path.abspath(".."))

from dkmonitor.utilities.db_interface import DbViewer
from dkmonitor.config.config_reader import ConfigReader

def get_user_change():
    pass


class AdminInterface(DbViewer):
    def __init__(self):
        config_reader = ConfigReader()
        self.settings = config_reader.configs_to_dict()
        super().__init__(self.settings["DataBase_Settings"]["database"],
                         self.settings["DataBase_Settings"]["user_name"],
                         self.settings["DataBase_Settings"]["password"],
                         self.settings["DataBase_Settings"]["host"])

    def display_user(self, user_name):
        user_stats = self.get_user_stats(user_name)
        if user_stats != {}:
            print("User Name: {}".format(user_stats["user_name"]))
            for system, disks in user_stats["systems"].items():
                print("|System Name: {}".format(system))
                for disk, d_stats in disks.items():
                    print("||Disk Name: {}".format(disk))
                    if d_stats[6] > 1:
                        colored_size = termcolor.colored(str(d_stats[4]/1024/1024/1024), "red")
                    else:
                        colored_size = termcolor.colored(str(d_stats[4]/1024/1024/1024), "green")
                    print("|||Total File Size    : {} GB".format(colored_size))
                    if d_stats[8] > 1:
                        colored_access = termcolor.colored(str(d_stats[7]), "red")
                    else:
                        colored_access = termcolor.colored(str(d_stats[7]), "green")
                    print("|||Last Access Average: {} days".format(colored_access))

        else:
            print("User Not found")

    def display_system(self, system_name):
        system_stats = self.get_system_stats(system_name)
        if system_stats != {}:
            print("System Name: {}".format(system_stats["system_name"]))
            for disk, d_stats in system_stats["disks"].items():
                print("|Disk Name: {}".format(disk))
                if d_stats['disk_stats'][5] > 1:
                    colored_size = termcolor.colored(str(d_stats['disk_stats'][3]/1024/1024/1024), "red")
                else:
                    colored_size = termcolor.colored(str(d_stats['disk_stats'][3]/1024/1024/1024), "green")
                print("||Total File Size    : {} GB".format(colored_size))

                if d_stats['disk_stats'][7] > 1:
                    colored_access = termcolor.colored(str(d_stats['disk_stats'][6]), "red")
                else:
                    colored_access = termcolor.colored(str(d_stats['disk_stats'][6]), "green")
                print("||Last Access Average: {} days".format(colored_access))

                print("|Users on: {}".format(disk))
                for user in d_stats["users"]:
                    print("|| {}".format(user))
        else:
            print("System Not Found")


def main():
    admin_int = AdminInterface()
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("display_flag", help="Specify what to display: system(s) or user(s)")
    parser.add_argument("display_name", help="Name of system or user you want to search for")
    args = parser.parse_args()
    if args.display_flag == "system":
        admin_int.display_system(args.display_name)
    elif args.display_flag == "user":
        admin_int.display_user(args.display_name)
    else:
        raise "Error: display_flag must either be 'user' or 'system'"




if __name__ == "__main__":
    adint = AdminInterface()
    #adint.display_user("rclaire")
    #adint.display_system("Circe")
    main()

