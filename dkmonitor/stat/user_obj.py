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
                 datetime=None,
                 total_file_size=None,
                 use_percent=None,
                 use_percent_change=0.0,
                 average_access=None,
                 avrg_access_change=0.0):

        StatObj.__init__(self,
                         "user_stats",
                         search_dir=search_dir,
                         system=system,
                         datetime=datetime,
                         total_file_size=total_file_size,
                         use_percent=use_percent,
                         use_percent_change=use_percent_change,
                         average_access=average_access,
                         avrg_access_change=avrg_access_change)

        self.collumn_dict["user_name"] = name

    def build_query_str(self):
        """Builds a string to query querying on user name, searched directory and system name."""

        query_str = ("user_name = '{user_name}' AND searched_directory"
                     " = '{searched_directory}' AND system = '{system}'")
        query_str = query_str.format(**self.collumn_dict)

        return query_str

    def email_user(self, emailer_obj, postfix, problem_lists, task_dict):
        """Emails the user associated with the object if they are flagged"""

        send_flag = False
        message = self.create_message(postfix)
        print(self.collumn_dict["user_name"])
        if self.collumn_dict["user_name"] in problem_lists[0]: #Adds top size use warning to message
            message.add_message("top_use_warning.txt", self.collumn_dict)
            send_flag = True
            print("BIG flag")
        if self.collumn_dict["user_name"] in problem_lists[1]: #Adds top old file warning to message
            message.add_message("top_old_warning.txt", self.collumn_dict)
            send_flag = True
            print("OLD flag")

        old_file_info = self.find_old_file_info(task_dict["last_access_threshold"])
        message_dict = task_dict.copy()
        message_dict.update(old_file_info)
        if old_file_info["old_file_count"] > 0:
            message.add_message("file_move_warning.txt", message_dict)
            send_flag = True
            print("REG flag")

        if send_flag is True:
            message.build_message()
            emailer_obj.send_email(message)

        print(self.collumn_dict["total_file_size"])
        print(self.collumn_dict["last_access_average"])
        print(problem_lists)
        print("-----------------------")


    def create_message(self, postfix):
        """Creates message to be sent to user"""

        address = self.collumn_dict["user_name"] + "@" + postfix
        message = Email(address, self.collumn_dict)

        return message

    def find_old_file_info(self, last_access_threshold):
        """Gathers data on the user's old files"""

        total_old_file_size = 0
        count = 0
        for file_path in self.file_list:
            if file_path.last_access > last_access_threshold:
                total_old_file_size += file_path.file_size
                count += 1

        return {"total_old_file_size": total_old_file_size/1024/1024/1024, "old_file_count": count}


