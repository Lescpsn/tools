import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart


class EmailSender:
    def __init__(self, sender, password, smtp_host, smtp_port=465):
        self.sender = sender
        self.pwd = password
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.has_sender = True

    @staticmethod
    def set_proxy(host, port):
        import socks
        import socket

        socket.socket = socks.socksocket
        socks.set_default_proxy(
            proxy_type=socks.PROXY_TYPE_HTTP,
            addr=host,
            port=port if isinstance(port, int) else int(port)
        )

    def send(self, receiver, subject, email_parts):
        assert isinstance(email_parts, dict), 'email_parts is dict of email parts, including text, html and image'

        mime_root = MIMEMultipart('related')
        mime_root['From'] = self.sender
        mime_root['To'] = receiver
        mime_root['Subject'] = subject
        mime_root.preamble = 'This is a multi-part message in MIME format.'
        mime_email = MIMEMultipart('alternative')
        mime_root.attach(mime_email)

        if 'text' in email_parts:
            email_part = self.__get_mime_text(email_parts.get('text'))
            mime_email.attach(email_part)
        if 'html' in email_parts:
            email_part = self.__get_mime_html(email_parts.get('html'))
            mime_email.attach(email_part)
        if 'image' in email_parts:
            email_part = self.__get_mime_image(email_parts.get('image'))
            mime_email.attach(email_part)

        return self.__send(receiver, mime_root)

    def __send(self, receiver, email):
        try:
            stmp = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            stmp.login(self.sender, self.pwd)
            stmp.sendmail(self.sender, receiver, email.as_string())
            stmp.quit()
            print(f'email >> send email to {receiver}')
            return True, (self.sender, receiver)
        except smtplib.SMTPException as e:
            print(f'email >> fail to send email: {e}')
            return False, (self.sender, receiver, str(e))

    @staticmethod
    def __get_mime_text(content):
        mime = MIMEText(content, _subtype='plain', _charset='utf-8')
        return mime

    @staticmethod
    def __get_mime_html(content):
        mime = MIMEText(content, _subtype='html', _charset='utf-8')
        return mime

    @staticmethod
    def __get_mime_image(img_path):
        with open(img_path, 'rb') as file:
            mime = MIMEImage(file.read())
            mime.add_header('Content-ID', '<image1>')
            return mime
