import stat_obj

class Directory(stat_obj.Stat_obj):
    def __init__(self,
            search_dir=None,
            datetime=None,
            total_file_size=None,
            use_percent=None,
            use_percent_change=0.0,
            average_access=None,
            avrg_access_change=0.0
            ):

        stat_obj.Stat_obj.__init__(self,
                "directory_stats",
                search_dir = search_dir,
                datetime = datetime,
                total_file_size = total_file_size,
                use_percent = use_percent,
                use_percent_change = use_percent_change,
                average_access = average_access,
                avrg_access_change = avrg_access_change
                )

    def build_query_str(self):
        query_str = "searched_directory = '{sdir}'".format(
                sdir=self.collumn_dict["searched_directory"])
        return query_str

    def save_data(self):
        self.calculate_stats()
        join_list = [
                str(self.collumn_dict["datetime"]),
                self.collumn_dict["searched_directory"],
                str(self.collumn_dict["total_file_size"]),
                str(self.collumn_dict["disk_use_percent"]),
                str(self.collumn_dict["last_access_average"])
            ]

        return " ".join(join_list)


