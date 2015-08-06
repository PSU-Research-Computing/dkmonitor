"""
This file contains the Email class. Each class acts as a separate message
This class allows you to build customized messages that can be sent by a different object
"""
import os

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Email:
    """
    Them Email class allows the program to build customized messages automatically.
    The objects are meant to be sent to an emailer object as a string to be mailed
    """

    def __init__(self, address, data_dict):
        self.body = ""
        self.add_message("main_message.txt", data_dict)

        self.msg = MIMEMultipart()
        self.msg["To"] = address
        self.msg["Subject"] = "Usage Warning on {system}".format(**data_dict)

    def build_message(self):
        """Attaches all the body string to the message"""

        body = MIMEText(self.body, 'plain')
        self.msg.attach(body)

    def add_message(self, message_file, data_dict):
        """Loads a pre-written message from external file and adds info to it from data_dict"""

        try:
            message_dir = os.path.abspath(".") + "/emailers/messages/"
            with open(message_dir + message_file, 'r') as mfile:
                message_str = mfile.read()

            self.body += message_str.format(**data_dict)
        except IOError as err:
            #TODO Add logging
            print(err)

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
