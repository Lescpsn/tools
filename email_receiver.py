from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr
import poplib
import re
import base64


class EmailReceiver:
    def __init__(self, email_addr, password, pop3_server):
        self.server = poplib.POP3(pop3_server)
        self.server.user(email_addr)
        self.server.pass_(password)
        self.email_cnt, _ = self.server.stat()

    def quit(self):
        self.server.quit()

    def delete_email(self, index):
        self.server.dele(index)

    def read_emails(self):
        email_list = list()
        for i in range(self.email_cnt):
            resp, lines, octets = self.server.retr(i + 1)
            email = b'\n'.join(lines).decode('utf-8')
            email = Parser().parsestr(email)
            data = {
                'index': i + 1,
                'size': octets,
                'from_name': '',
                'from_addr': '',
                'subject': '',
                'plain': '',
                'html': '',
                'attachment': list()
            }

            # parse email sender
            from_info = email.get('From', '')
            from_info, addr = parseaddr(from_info)
            name = self.__parse_basic(from_info)
            data.update(from_name=name)
            data.update(from_addr=addr)

            # parse subject
            subject_info = email.get('Subject', '')
            subject = self.__parse_basic(subject_info)
            data.update(subject=subject)

            # parse content
            self.__parse_content(email, data)
            email_list.append(data)
        return email_list

    @staticmethod
    def __parse_basic(basic):
        basic, charset = decode_header(basic)[0]
        return basic.decode(charset) if charset else basic

    def __parse_content(self, email, data):
        if email.is_multipart():
            for part in email.get_payload():
                self.__parse_content(part, data)
        else:
            content = email.get_payload()
            content_type = email.get_content_type()
            charset = email.get_content_charset()

            # get content encoding
            email_str = email.__str__()
            findall = re.findall(r'Content-Transfer-Encoding: (.*?)\n', email_str)
            if findall:
                content_encoding = findall[0]
            else:
                return

            # parse detail
            if content_type == 'text/plain':
                content = base64.b64decode(content) if content_encoding == 'base64' else content
                content = str(content, charset, errors='ignore') if content_encoding == 'base64' else content
                data.update(plain=content)
            if content_type == 'text/html':
                content = base64.b64decode(content) if content_encoding == 'base64' else content
                content = str(content, charset, errors='ignore') if content_encoding == 'base64' else content
                data.update(html=content)
            else:
                findall = re.findall(r'attachment; filename=(.*?)\n', email_str)
                if findall:
                    file_name = findall[0]
                    file_name = file_name.replace('"', '')
                    data.get('attachment').append((file_name, content))
