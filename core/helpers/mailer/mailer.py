#!/usr/bin/python

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart



class Mailer:
    def __init__(self):
        self.username = "justwebagency"
        self.password = "3q6POFgRHhFy"
        self.sender = "automation@justwebagency.com"
        self.CARS_RECIPIENTS = [
            "anton@justwebagency.com",
            "dima@justwebagency.com",
            "iammarykatesmith@gmail.com",
        ]

    def send_mail(
        self,
        project,
        text_message,
        subject,
        recipients=None,
    ):
        if not recipients:
            recipients = self.CARS_RECIPIENTS

        msg = MIMEMultipart("mixed")
        msg["Subject"] = f"{project} {subject}"
        msg["From"] = self.sender
        msg["To"] = ", ".join(recipients)

        text_message = MIMEText(text_message, "html")
        msg.attach(text_message)

        mail_server = smtplib.SMTP("mail.smtp2go.com", 2525)
        mail_server.ehlo()
        mail_server.starttls()
        mail_server.ehlo()
        mail_server.login(self.username, self.password)
        mail_server.sendmail(self.sender, recipients, msg.as_string())
        mail_server.close()
