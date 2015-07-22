import re
import os
import shutil
import stat_obj
import email_obj

class User(stat_obj.Stat_obj):
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

        stat_obj.Stat_obj.__init__(self,
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
        query_str = "user_name = '{name}' AND searched_directory = '{sdir}' AND system = '{sys}'"
        query_str = query_str.format(name=self.collumn_dict["user_name"],
                         sdir=self.collumn_dict["searched_directory"],
                         sys=self.collumn_dict["system"])

        return query_str

    def email_user(self, emailer_obj, postfix, access_threshold, problem_lists):
        old_info = self.find_old_info(access_threshold)
        message = self.create_message(postfix)
        if self.collumn_dict["user_name"] in problem_lists[0]: #Adds top size use warning to message
            message.add_top_use_warning(self.collumn_dict["total_file_size"])
        if self.collumn_dict["user_name"] in problem_lists[1]: #Adds top old file warning to message
            message.add_top_old_warning(self.collumn_dict["last_access_average"], self.collumn_dict["disk_use_percent"])

        if old_file_info[1] > 0:
            message.add_access_warning(old_file_info, access_threshold) #Adds general old file warning to message
            message.build_message()
            emailer_obj.send_email(message)


    def create_message(self, postfix):
        address = self.collumn_dict["user_name"] + "@" + postfix
        message = email_obj.Email(address,
                                  self.collumn_dict["system"],
                                  self.collumn_dict["searched_directory"])

        return message

    def find_old_info(self, access_threshold):
        total_old_file_size = 0
        count = 0
        for fi in self.file_list:
            if fi.last_access > access_threshold:
                total_old_file_size += fi.file_size
                count += 1

        return [total_old_file_size, count]


    #Moves old files over to an archive disk while hopefuly maintaining file structure
    def move_old_files(self, move_to, old_threshold):
        root_dir = move_to + self.collumn_dict["user_name"] + "_oldFiles"
        if not os.path.exists(root_dir):
            os.mkdir(root_dir)
        for fi in self.file_list:
            if fi.last_access >= old_threshold:
                new_file_path = re.sub("^{old_path}", root_dir, fi.file_path)
                last = new_file_path.rfind('/')
                dir_path = new_file_path[:last]
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)
                shutil.move(fi.file_path, new_file_path)



    def save_data(self):
        self.calculate_stats()
        join_list = [self.collumn_dict["user_name"],
                     str(self.collumn_dict["datetime"]),
                     self.collumn_dict["searched_directory"],
                     str(self.collumn_dict["total_file_size"]),
                     str(self.collumn_dict["disk_use_percent"]),
                     str(self.collumn_dict["last_access_average"])]

        return " ".join(join_list)

