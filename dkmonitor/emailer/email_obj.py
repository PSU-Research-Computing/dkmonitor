"""
This file contains the Email class. Each class acts as a separate message
This class allows you to build customized messages that can be sent by a different object
"""

import sys, os
sys.path.append(os.path.abspath("../.."))
from dkmonitor.utilities import log_setup

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Email:
    """
    Them Email class allows the program to build customized messages automatically.
    The objects are meant to be sent to an emailer object as a string to be mailed
    """

    def __init__(self, address, data_dict):
        self.logger = log_setup.setup_logger("email_log.log")

        self.body = ""
        self.add_message("main_message.txt", data_dict)

        self.msg = MIMEMultipart()
        self.msg["To"] = address
        self.msg["Subject"] = "Usage Warning on {system}".format(**data_dict)

    def build_and_send_message(self):
        """Attaches all the body string to the message"""

        body = MIMEText(self.body, 'plain')
        self.msg.attach(body)

        server = smtplib.SMTP('localhost')
        server.sendmail("Do-Not-Reply", "wpatt2@pdx.edu", self.msg.as_string())
        #self.server.sendmail(self.user_name, message["To"], message.as_string())

    def add_message(self, message_file, data_dict):
        """Loads a pre-written message from external file and adds info to it from data_dict"""

        message_file = os.path.abspath(".") + "/emailers/messages/" + message_file
        try:
            with open(message_file, 'r') as mfile:
                message_str = mfile.read()
            self.body += message_str.format(**data_dict)

        except IOError as err:
            self.logger.error("File %s does not exist", message_file)
            print(err)
        except KeyError as key:
            self.logger.error("Key %s does not exist", key)
            print (message_str)
            for key in data_dict.keys():
                print(key)
            raise key


    def attach_file_stream(self, stream, attached_file_name):
        """
        This method allows you to attach a file to a message
        ***NOT USED***
        """

        stream.seek(0)
        attachment = MIMEText(stream.read())
        attachment.add_header('Content-Disposition', 'attachment', filename=attached_file_name)
        self.msg.attach(attachment)

