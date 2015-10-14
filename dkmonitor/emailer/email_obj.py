"""
This file contains the Email class. Each class acts as a separate message
This class allows you to build customized messages that can be sent by a different object
"""

import sys, os
sys.path.append(os.path.abspath("../.."))
#sys.path.append(os.path.realpath(__file__)[:os.path.realpath(__file__).rfind("/")] + "/")
from dkmonitor.utilities import log_setup

import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Email:
    """
    Them Email class allows the program to build customized messages automatically.
    The objects are meant to be sent to an emailer object as a string to be mailed
    """

    def __init__(self, address, data_dict):
        self.logger = log_setup.setup_logger(__name__)

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
        server.sendmail("Do-Not-Reply", self.msg["To"], self.msg.as_string())

    def add_message(self, message_file, data_dict):
        """Loads a pre-written message from external file and adds info to it from data_dict"""

        message_file = os.path.abspath(".") + "/emailer/messages/" + message_file
        for key, item in data_dict.items():
            if isinstance(item, float):
                data_dict[key] = round(data_dict[key], 2)

        try:
            with open(message_file, 'r') as mfile:
                message_str = mfile.read()
            self.body += message_str.format(**data_dict)

        except IOError as err:
            self.logger.error("File %s does not exist", message_file)
        except KeyError as keyerr:
            m = re.search("'([^']*)'", keyerr.message)
            key = m.group(1)
            self.logger.error("Key %s does not exist", key)
            raise keyerr


    def attach_file_stream(self, stream, attached_file_name):
        """
        This method allows you to attach a file to a message
        ***NOT USED***
        """

        stream.seek(0)
        attachment = MIMEText(stream.read())
        attachment.add_header('Content-Disposition', 'attachment', filename=attached_file_name)
        self.msg.attach(attachment)

