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
            avrg_access_change=0.0
            ):

        stat_obj.Stat_obj.__init__(self,
                "user_stats",
                search_dir = search_dir,
                system = system,
                datetime = datetime,
                total_file_size = total_file_size,
                use_percent = use_percent,
                use_percent_change = use_percent_change,
                average_access = average_access,
                avrg_access_change = avrg_access_change
                )

        self.collumn_dict["user_name"] = name

    def build_query_str(self):
        query_str = "user_name = '{name}' AND searched_directory = '{sdir}' AND system = '{sys}'".format(
                name=self.collumn_dict["user_name"],
                sdir=self.collumn_dict["searched_directory"],
                sys=self.collumn_dict["system"]
                )
        return query_str

    def email_user(self, emailer_obj, postfix, access_day_threshold, file_size_threshold, percentage_threshold):

        message = None
        if (access_day_threshold > 0) and (access_day_threshold <= self.collumn_dict["last_access_average"]):
            #TODO This method needs to get a list of old files, save their paths to a file
            #TODO and attach them to the email document
            if message == None:
                message = self.create_message(postfix)
            old_file_stream = self.build_old_file_attachment(access_day_threshold)
            message.add_access_warning(self.collumn_dict["last_access_average"], access_day_threshold, old_file_stream)

        if (file_size_threshold > 0) and (file_size_threshold <= self.collumn_dict["total_file_size"]):
            if message == None:
                message = self.create_message(postfix)
            message.add_size_warning(self.collumn_dict["total_file_size"], file_size_threshold)

        if (percentage_threshold > 0) and (percentage_threshold <= self.collumn_dict["disk_use_percent"]):
            if message == None:
                message = self.create_message(postfix)
            message.add_percent_warning(self.collumn_dict["disk_use_percent"], percentage_threshold)

        if message != None:
            emailer_obj.send_email(message)

    def create_message(self, postfix):
        address = self.collumn_dict["user_name"] + "@" + postfix
        message = email_obj.Email(
                address,
                self.collumn_dict["system"],
                self.collumn_dict["searched_directory"])

        return message

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








