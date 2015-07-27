import smtplib
import settings_obj
import sys


class emailer:
    def __init__(self, suffix):
        self.suffix = suffix

    def send_email(self, message):
        server = smtplib.SMTP('localhost')
        server.sendmail("Do-Not-Reply", "wpatt2@pdx.edu", message.as_string())
        #self.server.sendmail(self.user_name, message["To"], message.as_string())

