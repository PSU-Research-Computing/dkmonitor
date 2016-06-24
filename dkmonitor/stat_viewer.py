"""
Admin interface is a Command Line interface for Administrators
that want to view user and system information
"""

import termcolor, argparse

import sys, os
sys.path.append(os.path.abspath(".."))

from dkmonitor.database_manager import DataBase, DirectoryStats, UserStats
from dkmonitor.config.settings_manager import export_settings


class AdminStatViewer(DataBase):
    """
    AdminStatViewer is an extention of DataBase that provieds
    an interface for viewing directory and user statistics stored
    in the shared database
    """

    def __init__(self, db_settings):
        super().__init__(hostname=db_settings["hostname"],
                         database=db_settings["database"],
                         password=db_settings["password"],
                         username=db_settings["username"],
                         db_type=db_settings["db_type"])

    @staticmethod
    def print_color_key():
        """Print the color key"""
        print("Color Key----------")
        green = termcolor.colored("green", "green")
        print("{} == Decrease".format(green))
        yellow = termcolor.colored("yellow", "yellow")
        print("{} == No Change".format(yellow))
        red = termcolor.colored("red", "red")
        print("{} == Increase".format(red))
        print("-------------------")

    def display_user(self, username):
        """
        Displays user stats in color with information gathered by the
        DbViewer object from the dkmonitor database
        """
        session = self.create_session()
        disks_on_user = [disk[0] for disk in session.query(UserStats.target_path).\
                                             filter(UserStats.username == username).\
                                             distinct()]
        hosts_on_user = [host[0] for host in session.query(UserStats.hostname).\
                                             filter(UserStats.username == username).\
                                             distinct()]

        user_stats = []
        for disk in disks_on_user:
            for host in hosts_on_user:
                user_stats.append(session.query(UserStats).
                                  filter(UserStats.username == username).\
                                  filter(UserStats.target_path == disk).\
                                  filter(UserStats.hostname == host).\
                                  order_by(UserStats.datetime.desc()).limit(2).all())

        self.print_color_key()
        if user_stats != []:
            total_file_size = 0
            average_file_age = 0
            print("User Name: {}".format(username))
            for disk in user_stats:
                print("|System Name: {}".format(disk[0].hostname))
                print("||Disk Name: {}".format(disk[0].target_path))

                self.print_size_age_change(disk)
                total_file_size += disk[0].total_file_size
                average_file_age += disk[0].average_file_age

                print("")

            print("|Total File Size : {} GB".format(round(total_file_size/1024/1024/1024, 2)))
            print("|Average File Age: {} days".format(round(average_file_age/len(user_stats), 2)))

        else:
            print("User '{}' Not found".format(username), file=sys.stderr)

        session.close()

    def display_system(self, hostname):
        """
        Displays system stats in color with information gathered by the
        DbViewer object from the dkmonitor database
        """
        session = self.create_session()
        disks_on_system = [disk[0] for disk in session.query(DirectoryStats.target_path).\
                                               filter(DirectoryStats.hostname == hostname).\
                                               distinct()]
        system_disk_stats = []
        for disk in disks_on_system:
            system_disk_stats.append(session.query(DirectoryStats).\
                                     filter(DirectoryStats.hostname == hostname).\
                                     filter(DirectoryStats.target_path == disk).\
                                     order_by(DirectoryStats.datetime.desc()).limit(2).all())

        self.print_color_key()
        if system_disk_stats != []:
            total_file_size = 0
            average_file_age = 0
            print("System Name        : {}".format(hostname))
            for disk in system_disk_stats:
                print("|Disk Name         : {}".format(disk[0].target_path))
                self.print_size_age_change(disk)
                print("|Users on: {}".format(disk[0].target_path))
                for username in session.query(UserStats.username).\
                                filter(UserStats.hostname == hostname).\
                                filter(UserStats.target_path == disk[0].target_path).\
                                distinct():
                    print("|| {}".format(username[0]))

                total_file_size += disk[0].total_file_size
                average_file_age += disk[0].average_file_age

            print("|Total File Size : {} GB".format(round(total_file_size/1024/1024/1024, 2)))
            print("|Average File Age: {} days".format(round(average_file_age/len(system_disk_stats),
                                                            2)))
        else:
            print("System '{}' Not Found".format(hostname), file=sys.stderr)

        session.close()

    @staticmethod
    def get_color(difference):
        """Returns color string based on the difference of two values"""
        if difference > 1:
            color = "green"
        elif difference == 1:
            color = "yellow"
        elif difference < 1:
            color = "red"
        return color

    def print_size_age_change(self, rows):
        """Prints size and file age change in color for a row from the db"""
        try:
            size_change = rows[0].total_file_size / rows[1].total_file_size
            size_color = self.get_color(size_change)
            age_change = rows[0].average_file_age / rows[1].average_file_age
            age_color = self.get_color(age_change)
        except IndexError:
            age_color, size_color = 'yellow', 'yellow'

        colored_size = termcolor.colored(str(round(rows[0].total_file_size/1024/1024/1024, 2)),
                                         size_color)
        print("||Total File Size  : {} GB".format(colored_size))

        colored_access = termcolor.colored(str(round(rows[0].average_file_age, 2)), age_color)
        print("||Average File Age : {} days".format(colored_access))

    def display_users(self):
        """Displays all users"""
        session = self.create_session()
        user_num = len([print(username[0]) for username in session.query(UserStats.username).\
                                                           distinct()])
        if user_num == 0:
            print("There are currently no users in the userstats table")
        session.close()

    def display_systems(self):
        """Displays all systems"""
        session = self.create_session()
        host_num = len([print(hostname[0]) for hostname in session.query(DirectoryStats.hostname).\
                                                           distinct()])
        if host_num == 0:
            print("There are currently no systems in the directorystats table")
        session.close()


def get_args(args):
    """Gets args from argparse"""
    description = ("Administrator Interface is a program That allows you to view system and user"
                   " data stored in a central database managed by the appilcation dkmonitor")
    parser = argparse.ArgumentParser(description=description)

    subparsers = parser.add_subparsers()
    system_parser = subparsers.add_parser("system")
    system_parser.set_defaults(which="system")
    system_parser.add_argument("system_host_name",
                               help="Name of system you want to search for")

    user_parser = subparsers.add_parser("user")
    user_parser.set_defaults(which="user")
    user_parser.add_argument("user_name",
                             help="Name of user you want to search for")

    all_parser = subparsers.add_parser("all")
    all_parser.set_defaults(which="all")
    all_parser.add_argument("display_name",
                            help="Specify either 'systems' or 'users' to display all found matchs")

    return parser.parse_args(args)


def main(args=None):
    """Main function that runs the command line interface"""
    if args is None:
        args = sys.argv[1:]

    db_settings = export_settings()["DataBase_Settings"]
    admin_int = AdminStatViewer(db_settings)
    args = get_args(args)

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
    main()

