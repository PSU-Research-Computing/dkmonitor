from email.mime.multipart import MIMEMultipart

class Email:
    def __init__(self, address, system, directory):
        self.address = address
        self.system = system
        self.directory = directory

        self.body = ""

        self.msg = MIMEMultipart
        self.msg["To"] = self.address
        self.msg["Subject"] = "Usage Warning on {sys}".format(sys=self.system)

    def build_message(self, last_access, file_size, use_percentage):
        #TODO Implement this method next
        pass

    def main_message(self):
        message = """
        Dear {user},
        You have been flagged for improper use of {dk} on {sys}. Please address the message(s) below to fix the problem.
        """.format(user=self.address, dk=self.directory, sys=self.system)
        self.body += message

    def add_access_warning(self, last_access, threshold):
        #TODO this method also needs to be able to add an attached file with all old file paths
        #TODO The file attachment could possibly be in an other method
        #TODO Also need to address deleting the file after its sent to the user.
        message = """
        The average last access time for all of your files is too high.
        Your access average: {acc}
        Max access average: {thresh}
        A file is attached to this email with all of your old files that need to either be
        deleted, moved or used.
        """.format(acc=last_access, thresh=threshold)
        self.body += message

    def add_size_warning(self, total_size, threshold):
        message = """
        The total size of all your files is too large.
        Your total file size: {size}
        Max total file size: {max_size}
        Please delete or move some of your data.
        """.format(size=total_size, max_size=threshold)
        self.body += message

    def add_percent_warning(self, percent, threshold):
        message = """
        You are using to large of a percentage of disk space.
        Your disk use percentage: {per}%
        Max disk use percent: {max_percent}%
        Please delete or move some of your data.
        """.format(per=percent, max_percent=threshold)
        self.body += message

