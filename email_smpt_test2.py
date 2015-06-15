import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)

server.ehlo()
server.starttls()
server.ehlo()

server.login("wpatt2@pdx.edu", "easyJIMb0")

server.sendmail("wpatt2@pdx.edu", "willsnore@gmail.com", "testmessage")
