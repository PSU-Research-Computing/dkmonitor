"""
This file contains the emailer class.
The emailer takes messages and sends them out
"""

import smtplib

class Emailer:
    """
    Emailer is the interface between the email server and the program
    This class is meant to be extened to different email APIs if nesseary
    That is why it is so short and seemingly pointless
    """

    def __init__(self, suffix):
        self.suffix = suffix

    def send_email(self, message):
        """Creates a server and sends the message passed in"""

        server = smtplib.SMTP('localhost')
        server.sendmail("Do-Not-Reply", "wpatt2@pdx.edu", message.as_string())
        #self.server.sendmail(self.user_name, message["To"], message.as_string())

