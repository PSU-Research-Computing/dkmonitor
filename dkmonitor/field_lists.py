"""
"""

class FieldLists():
    def __init__(self):
        self.task_fields = ["system_name",
                            "directory_path",
                            "file_relocation_path",
                            "disk_use_percent_threshold",
                            "email_users",
                            "last_access_threshold",
                            "bad_flag_percent"]

        self.db_fields = ["user_name",
                          "password",
                          "database",
                          "host",
                          "purge_after_day_number"]

        self.thread_fields = ["thread_mode",
                              "thread_number"]

        self.email_fields = ["user_postfix"]

    def generate_task_fields(self):
        for i in self.task_fields:
            yield i

    def generate_db_fields(self):
        for i in self.db_fields:
            yield i

    def generate_thread_fields(self):
        for i in self.thread_fields:
            yield i

    def generate_email_fields(self):
        for i in self.email_fields:
            yield i
