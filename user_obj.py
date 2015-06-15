import stat_obj

class User(stat_obj.Stat_obj):
    def __init__(self,
            name,
            search_dir=None,
            datetime=None,
            total_file_size=None,
            use_percent=None,
            use_percent_change=0.0,
            average_access=None,
            avrg_access_change=0.0
            ):

        stat_obj.Stat_obj.__init__(self,
                "user_stats",
                search_dir = search_dir,
                datetime = datetime,
                total_file_size = total_file_size,
                use_percent = use_percent,
                use_percent_change = use_percent_change,
                average_access = average_access,
                avrg_access_change = avrg_access_change
                )

        self.collumn_dict["user_name"] = name

    def build_query_str(self):
        query_str = "user_name = '{name}' AND searched_directory = '{sdir}'".format(
                name=self.collumn_dict["user_name"],
                sdir=self.collumn_dict["searched_directory"])
        return query_str

    def email_user(self, email_obj, access_day_threshold, file_size_threshold, percentage_threshold):
        #if access_day_threshold >= self.collumn_dict["last_access_average"]:
        email_obj.send_email(self.collumn_dict["user_name"])
        #TODO left off here. Need to work on flagging users to send emails.

    def save_data(self):
        self.calculate_stats()
        join_list = [
                self.collumn_dict["user_name"],
                str(self.collumn_dict["datetime"]),
                self.collumn_dict["searched_directory"],
                str(self.collumn_dict["total_file_size"]),
                str(self.collumn_dict["disk_use_percent"]),
                str(self.collumn_dict["last_access_average"])
            ]

        return " ".join(join_list)








