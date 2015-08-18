"""
This Script collects and processing information on a user's usage on a
disk or in a directory
"""

import sys, os
sys.path.append(os.path.abspath("../.."))

from dkmonitor.stat.stat_obj import StatObj
from dkmonitor.emailers.email_obj import Email

class User(StatObj):
    """
    This class stores data about one user on a system
    It can email them if they are flagged
    Process Their stats after their data is collected
    And then store the stats in a database
    """

    def __init__(self,
                 name,
                 search_dir=None,
                 system=None,
                 datetime=None):

        StatObj.__init__(self,
                         "user_stats",
                         search_dir=search_dir,
                         system=system,
                         datetime=datetime)

        self.collumn_dict["user_name"] = name

    def build_query_str(self):
        """Builds a string to query querying on user name, searched directory and system name."""

        query_str = ("user_name = '{user_name}' AND searched_directory"
                     " = '{searched_directory}' AND system = '{system}'")
        query_str = query_str.format(**self.collumn_dict)

        return query_str

    def email_user(self, postfix, problem_lists, task_dict, current_use):
        """Emails the user associated with the object if they are flagged"""

        if current_use > task_dict["Threshold_Settings"]["disk_use_percent_warning_threshold"]:
            send_flag = False
            if task_dict["Email_Settings"]["email_usage_warnings"] == "yes":
                message = self.create_message(postfix)
                print(self.collumn_dict["user_name"])
                if self.collumn_dict["user_name"] in problem_lists[0]:
                    message.add_message("top_use_warning.txt", self.collumn_dict)
                    send_flag = True
                    print("BIG flag")
                if self.collumn_dict["user_name"] in problem_lists[1]:
                    message.add_message("top_old_warning.txt", self.collumn_dict)
                    send_flag = True
                    print("OLD flag")

            if task_dict["Email_Settings"]["email_data_alteration_notices"] == "yes":
                message_dict = task_dict["System_Settings"].copy()
                message_dict.update(task_dict["Threshold_Settings"])
                message_dict.update(task_dict["Scan_Settings"])
                message_dict.update(self.stat_dict)
                message_dict["total_old_file_size"] = self.stat_dict["total_old_file_size"] / 1024 / 1024 / 1024
                if self.stat_dict["number_of_old_files"] > 0:
                    if current_use > task_dict["Threshold_Settings"]["disk_use_percent_critical_threshold"]:
                        message.add_message("file_move_notice.txt", message_dict)
                        print("MOVE_NOTICE")
                    else:
                        message.add_message("file_move_warning.txt", message_dict)
                        print("REG flag")

                    send_flag = True

            if send_flag is True:
                message.build_and_send_message()

            print(self.collumn_dict["total_file_size"])
            print(self.collumn_dict["last_access_average"])
            print(problem_lists)
            print("-----------------------")


    def create_message(self, postfix):
        """Creates message to be sent to user"""

        address = self.collumn_dict["user_name"] + "@" + postfix
        message = Email(address, self.collumn_dict)

        return message

