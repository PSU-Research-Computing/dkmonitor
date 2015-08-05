"""
This Script collects and processing information on a user's usage on a
disk or in a directory
"""

import dkmonitor.stat_obj as stat_obj
import dkmonitor.email_obj as email_obj

class User(stat_obj.StatObj):
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

        stat_obj.StatObj.__init__(self,
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

        query_str = "user_name = '{name}' AND searched_directory = '{sdir}' AND system = '{sys}'"
        query_str = query_str.format(name=self.collumn_dict["user_name"],
                                     sdir=self.collumn_dict["searched_directory"],
                                     sys=self.collumn_dict["system"])

        return query_str

    def email_user(self,
                   emailer_obj,
                   postfix,
                   last_access_threshold,
                   days_between_runs,
                   move_dir,
                   problem_lists):
        """Emails the user associated with the object if they are flagged"""

        old_file_info = self.find_old_file_info(last_access_threshold)
        message = self.create_message(postfix)
        print(self.collumn_dict["user_name"])
        if self.collumn_dict["user_name"] in problem_lists[0]: #Adds top size use warning to message
            message.add_top_use_warning(self.collumn_dict["total_file_size"],
                                        self.collumn_dict["disk_use_percent"])
            print("BIG flag")
        if self.collumn_dict["user_name"] in problem_lists[1]: #Adds top old file warning to message
            message.add_top_old_warning(self.collumn_dict["last_access_average"])
            print("OLD flag")

        if old_file_info[1] > 0:
            message.add_access_warning(old_file_info,
                                       last_access_threshold,
                                       days_between_runs,
                                       move_dir) #Adds general old file warning to message
            message.build_message()
            emailer_obj.send_email(message)
            print("REG flag")

        print(self.collumn_dict["total_file_size"])
        print(self.collumn_dict["last_access_average"])
        print(problem_lists)
        print("-----------------------")


    def create_message(self, postfix):
        """Creates message to be sent to user"""

        address = self.collumn_dict["user_name"] + "@" + postfix
        message = email_obj.Email(address,
                                  self.collumn_dict["system"],
                                  self.collumn_dict["searched_directory"])

        return message

    def find_old_file_info(self, last_access_threshold):
        """Gathers data on the user's old files"""

        total_old_file_size = 0
        count = 0
        for file_path in self.file_list:
            if file_path.last_access > last_access_threshold:
                total_old_file_size += file_path.file_size
                count += 1

        return [total_old_file_size, count]


