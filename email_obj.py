
class Email:
    def __init__(self, access_day_threshold, file_size_threshold, percentage_threshold):
        self.access_day_threshold = access_day_threshold
        self.file_size_threshold = file_size_threshold
        self.percentage_threshold = percentage_threshold

    def build_message(self, last_access, file_size, use_percentage):
        pass
