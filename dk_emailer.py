import smtplib
import settings_obj

server.sendmail("wpatt2@pdx.edu", "willsnore@gmail.com", "testmessage")

class emailer:
    def __init__(self, user_name, password, suffix):

        self.user_name = user
        self.password = passw
        self.suffix = suff

        self.server = smtplib.SMTP('smtp.gmail.com', 587)
        self.server.ehlo()
        self.server.starttls()
        self.server.ehlo()

        self.server.login(self.user_name, self.password)


    def send_email(self, prefix):
        server.sendmail(self.user_name, prefix + self.suffix, self.message(odin_name))

    def message(self, prefix):
        return_message ="""
        Dear {name},
        You have been flagged by ARC's monitoring software for you inaproprate use of the scratch space.
        Please review your usege (delete or move old files, move or delete large files).
        Thank you for your time,
        --ARC staff
        """.format(name=prefix)

        return return_message

