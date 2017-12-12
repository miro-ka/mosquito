import smtplib
import configargparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from premailer import transform


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
        # mail_to = self.recipients if type(self.recipients) is list else [self.recipients]
        mail_to = self.recipients

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = mail_from
        msg['To'] = mail_to

        # body = self.html_style() + body
        # msg.attach(MIMEText(body, 'html'))
        body = transform(body)
        #body = '<html> <h1 style="font-weight:bolder; border:1px solid black">Peter</h1> <p style="color:red">Hej</p> </html>'
        msg.attach(MIMEText(body, 'html'))
        mail = smtplib.SMTP("smtp.gmail.com", 587)
        mail.ehlo()
        mail.starttls()
        mail.login(self.username, self.password)
        mail.sendmail(mail_from, mail_to, msg.as_string())
        mail.close()
        print('mail successfully sent')

    @staticmethod
    def html_style():
        """
        Email css styles
        """
        style = '''
        <style>
            #headings {
            font-size:26px !important;
            line-height:32px !important;
            }
        </style>
        '''
        return style
