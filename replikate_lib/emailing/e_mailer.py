import getpass
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from typing import List, Tuple

from replikate_lib.emailing.mail_account import MailAccount
from replikate_lib.emailing.server_parameters import ServerParameters


class EMailer:
    def __init__(
            self,
            server_parameters: ServerParameters,
            mail_account: MailAccount
    ):
        self.server_parameters = server_parameters
        self.mail_account = mail_account
        self.pwd = None
        if server_parameters.authentication is not None:
            print(' | Required password for sending mail')
            self.pwd = getpass.getpass(' | Password for {}@{}: '.format(mail_account.user_name, server_parameters.host))

    def send_mail(self, receivers: List[str], subject: str, message: str, files: List[Tuple[str, str]] = []):
        if self.server_parameters.authentication == 'STARTTLS':
            context = ssl.create_default_context()
            try:
                with smtplib.SMTP(self.server_parameters.host, self.server_parameters.port) as smtp:
                    smtp.starttls(context=context)
                    smtp.login(
                        self.mail_account.user_name,
                        self.pwd
                    )
                    mail = MIMEMultipart()
                    mail['From'] = self.mail_account.mail
                    mail['To'] = ', '.join(receivers)
                    mail['Date'] = formatdate(localtime=True)
                    mail['Subject'] = subject
                    mail.attach(MIMEText(message, 'html'))
                    for (f, name) in files:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(open(f, 'rb').read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', 'piece; filename= %s' % name)
                        mail.attach(part)

                    smtp.sendmail(
                        self.mail_account.mail,
                        receivers,
                        mail.as_string()
                    )
            except smtplib.SMTPException as e:
                print('Cannot send email')