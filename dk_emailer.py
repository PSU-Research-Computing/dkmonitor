import smtplib
import settings_obj

#server.sendmail("wpatt2@pdx.edu", "willsnore@gmail.com", "testmessage")

class emailer:
    def __init__(self, user_name, password, suffix):

        self.user_name = user_name
        self.password = password
        self.suffix = suffix

        self.server = smtplib.SMTP('smtp.gmail.com', 587)
        self.server.ehlo()
        self.server.starttls()
        self.server.ehlo()

        self.server.login(self.user_name, self.password)

    #def build_and_send(self, access_val, file_size_val, percent_val):


    def send_email(self, message):
        self.server.sendmail(self.user_name, message["To"], message.as_string())
        #pass

    def message(self, prefix):
        return_message = """
        Dear {name},
        You have been flagged by ARC's monitoring software for you inaproprate use of the scratch space.
        Please review your usege (delete or move old files, move or delete large files).
        Thank you for your time,
        --ARC staff
        """.format(name=prefix)

        return return_message

