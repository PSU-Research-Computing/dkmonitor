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

    def print_color_key(self):
        print("Color Key----------")
        green = termcolor.colored("green", "green")
        print("{} == Decrease".format(green))
        yellow = termcolor.colored("yellow", "yellow")
        print("{} == No Change".format(yellow))
        red = termcolor.colored("red", "red")
        print("{} == Increase".format(red))
        print("-------------------")


    def display_user(self, user_name):
        self.print_color_key()
        user_stats = self.get_user_stats(user_name)
        if user_stats != {}:
            print("User Name: {}".format(user_stats["user_name"]))
            for system, disks in user_stats["systems"].items():
                print("|System Name: {}".format(system))
                for disk, d_stats in disks.items():
                    print("||Disk Name: {}".format(disk))
                    if d_stats[6] > 1:
                        colored_size = termcolor.colored(str(d_stats[4]/1024/1024/1024), "red")
                    elif d_stats[6] == 1:
                        colored_size = termcolor.colored(str(d_stats[4]/1024/1024/1024), "yellow")
                    else:
                        colored_size = termcolor.colored(str(d_stats[4]/1024/1024/1024), "green")
                    print("|||Total File Size    : {} GB".format(colored_size))
                    if d_stats[8] > 1:
                        colored_access = termcolor.colored(str(d_stats[7]), "red")
                    elif d_stats[8] == 1:
                        colored_size = termcolor.colored(str(d_stats[7]/1024/1024/1024), "yellow")
                    else:
                        colored_access = termcolor.colored(str(d_stats[7]), "green")
                    print("|||Last Access Average: {} days".format(colored_access))

        else:
            print("User Not found")

    def display_system(self, system_host_name):
        self.print_color_key()
        system_stats = self.get_system_stats(system_host_name)
        if system_stats != {}:
            print("System Name: {}".format(system_stats["system_host_name"]))
            for disk, d_stats in system_stats["disks"].items():
                print("|Disk Name: {}".format(disk))
                if d_stats['disk_stats'][5] > 1:
                    colored_size = termcolor.colored(str(d_stats['disk_stats'][3]/1024/1024/1024), "red")
                elif d_stats['disk_stats'][5] > 1:
                    colored_size = termcolor.colored(str(d_stats['disk_stats'][3]/1024/1024/1024), "yellow")
                else:
                    colored_size = termcolor.colored(str(d_stats['disk_stats'][3]/1024/1024/1024), "green")
                print("||Total File Size    : {} GB".format(colored_size))

                if d_stats['disk_stats'][7] > 1:
                    colored_access = termcolor.colored(str(d_stats['disk_stats'][6]), "red")
                elif d_stats['disk_stats'][7] == 1:
                    colored_access = termcolor.colored(str(d_stats['disk_stats'][6]), "yellow")
                else:
                    colored_access = termcolor.colored(str(d_stats['disk_stats'][6]), "green")
                print("||Last Access Average: {} days".format(colored_access))

                print("|Users on: {}".format(disk))
                for user in d_stats["users"]:
                    print("|| {}".format(user))
        else:
            print("System Not Found")

    def display_users(self):
        for user in self.get_all_users():
            print(user)

    def display_systems(self):
        for system in self.get_all_systems():
            print(system)



def main():
    admin_int = AdminInterface()
    parser = argparse.ArgumentParser(description="")

    subparser = parser.add_subparsers()
    system_parser = subparser.add_parser("system")
    system_parser.set_defaults(which="system")
    system_parser.add_argument("system_host_name", help="Name of system or user you want to search for")

    user_parser = subparser.add_parser("user")
    user_parser.set_defaults(which="user")
    user_parser.add_argument("user_name", help="Name of system or user you want to search for")

    all_parser = subparser.add_parser("all")
    all_parser.set_defaults(which="all")
    all_parser.add_argument("display_name", help="Name of system or user you want to search for")

    args = parser.parse_args()

    if args.which == "system":
        admin_int.display_system(args.system_host_name)
    elif args.which == "user":
        admin_int.display_user(args.user_name)
    elif args.which == "all":
        if args.display_name == "users":
            admin_int.display_users()
        elif args.display_name == "systems":
            admin_int.display_systems()
        else:
            print("ERROR: display_name must be either 'users' or 'system'")



if __name__ == "__main__":
    adint = AdminInterface()
    #adint.display_user("rclaire")
    #adint.display_system("Circe")
    main()

