"""
This file contains the Email class. Each class acts as a separate message
This class allows you to build customized messages that can be sent by a different object
"""

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Email:
    """
    Them Email class allows the program to build customized messages automatically.
    The objects are meant to be sent to an emailer object as a string to be mailed
    """

    def __init__(self, address, system, directory):
        self.address = address
        self.system = system
        self.directory = directory

        self.body = ""
        self.main_message()

        self.msg = MIMEMultipart()
        self.msg["To"] = self.address
        self.msg["Subject"] = "Usage Warning on {sys}".format(sys=self.system)

    def build_message(self):
        """Attaches all the body string to the message"""

        body = MIMEText(self.body, 'plain')
        self.msg.attach(body)

    def main_message(self):
        """This fucntion contains the main message as a string"""

        message = """
        Dear {user},
        You have been flagged for improper use of {dk} on {sys}.
        Please address the message(s) below to fix the problem.

        """.format(user=self.address, dk=self.directory, sys=self.system)
        self.body += message

    def add_access_warning(self, old_file_info, threshold, days_between_runs, move_dir):
        """This method adds an access warning to the main message if the user has been flagged"""

        old_file_info[0] = round(old_file_info[0] / 1024 / 1024 / 1024, 3)
        message = """
        WARNING: All files accessed more than {thresh} days ago will be moved to {move}
        You have {days} day(s) before your files will be moved.
        Number of old files: {old_num}
        Combined size of old files: {size} GBs

        """.format(old_num=old_file_info[1],
                   size=old_file_info[0],
                   thresh=threshold,
                   days=days_between_runs,
                   move=move_dir)
        self.body += message

    def add_top_use_warning(self, total_size, dk_usage):
        """This message is added if the user has been flagged for using to much space"""

        total_size = round(total_size / 1024 / 1024 / 1024, 3)
        dk_usage = round(dk_usage, 3)
        message = """
        WARNING: You have been flagged as a top space user of {dk} on {sys}.
        {dk} is over it's use threshold. Please reduce your data usage.
        Total size of all files: {size} GBs
        Total disk use: {dk_use} %

        """.format(dk=self.directory,
                   sys=self.system,
                   size=total_size,
                   dk_use=dk_usage)
        self.body += message

    def add_top_old_warning(self, access_arvg):
        """This message is added if the user has too many old files"""

        access_arvg = round(access_arvg, 2)
        message = """
        WARNING: You have been flagged as a top owner of old files in {dk} on {sys}.
        Please use or remove all of your old files or they will be removed for you.
        Last access average of all your files: {acc} days

        """.format(dk=self.directory, sys=self.system, acc=access_arvg)
        self.body += message

    def as_string(self):
        """Returns the message as a string"""

        return self.msg.as_string()

    def attach_file_stream(self, stream, attached_file_name):
        """
        This method allows you to attach a file to a message
        ***NOT USED***
        """

        stream.seek(0)
        attachment = MIMEText(stream.read())
        attachment.add_header('Content-Disposition', 'attachment', filename=attached_file_name)
        self.msg.attach(attachment)
