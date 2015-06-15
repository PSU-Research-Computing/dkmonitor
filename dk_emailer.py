import smtplib
import settings_obj

server.sendmail("wpatt2@pdx.edu", "willsnore@gmail.com", "testmessage")

class emailer(settings_obj.Settings_interface):
    def __init__(self):
        settings_obj.Settings_interface.__init__(self)

        self.server = smtplib.SMTP('smtp.gmail.com', 587)
        self.server.ehlo()
        self.server.starttls()
        self.server.ehlo()


        self.server.login(self.settings["Email_API"]["User_name"], self.settings["Email_API"]["Password"])


    def send_mail(self, odin_name):
        pass

