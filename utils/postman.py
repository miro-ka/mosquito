import smtplib
import configargparse
from termcolor import colored


class Postman:
    """
    Simple email/postman module
    ! Currently supported only for gmail
    """
    arg_parser = configargparse.get_argument_parser()
    arg_parser.add('--mail_username', help='Email username (supported only gmail)')
    arg_parser.add("--mail_password", help='Email password (supported only gmail)')
    arg_parser.add("--mail_recipients", help='Email recipients')

    def __init__(self):
        self.args = self.arg_parser.parse_known_args()[0]
        self.username = self.args.mail_username
        self.password = self.args.mail_password
        self.recipients = self.args.mail_recipients

    def send_mail(self, subject, body):
        """
        Send email to configured account with given subject and body
        """
        mail_from = self.username
        mail_to = self.recipients if type(self.recipients) is list else [self.recipients]

        # Prepare actual message
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s
            """ % (mail_from, ", ".join(mail_to), subject, body)
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(self.username, self.password)
        server.sendmail(mail_from, mail_to, message)
        server.close()
        print('successfully sent the mail')
