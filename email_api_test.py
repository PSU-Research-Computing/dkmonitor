from google.appengine.api import mail

message = mail.EmailMessage(sender="Example.com Support <wpatt2@pdx.edu>",
                            subject="Test")

message.to = "Albert Johnson <willsnore@gmail.com>"
message.body = """
Test email
"""

message.send()
