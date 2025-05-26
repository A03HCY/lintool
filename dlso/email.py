from .utils     import try_for, safecode
from .data      import EmailEndpoint
from imapclient import IMAPClient
from rich       import print
import datetime
import email

class EmailService:
    def __init__(self, endpoint: EmailEndpoint):
        self.endpoint = endpoint
        self.imap: IMAPClient = None

        self._init_imap()
    
    def _init_imap(self):
        self.imap = IMAPClient(
            host=self.endpoint.imap,
            ssl=self.endpoint.ssl
        )
        try:
            self.imap.login(
                username=self.endpoint.account,
                password=self.endpoint.authorization
            )
        except:
            print(f"[red]Login failed for {self.endpoint.account}[/red]")
            raise
    
    @property
    def folder(self):
        folders = []
        for i in self.imap.list_folders():
            name = i[2]
            try:
                info = self.imap.select_folder(name)
            except:
                print(f"[red]Failed to select folder '{name}'[/red]")
                continue
            folders.append({
                'name': name,
                'count': info[b'EXISTS'],
            })
        self.imap.select_folder('INBOX')
        return folders
    
    def search(
        self,
        folder: str = 'INBOX',
        since: str = None,
        before: str = None,
        unread_only: bool = False,
        read_only: bool = False,
    ):
        qury_temp = []
        if since:
            since = datetime.datetime.strptime(since, "%Y-%m-%d")
            qury_temp.extend(['SINCE', since])
        if before:
            before = datetime.datetime.strptime(before, "%Y-%m-%d")
            qury_temp.extend(['BEFORE', before])
        if unread_only and read_only == False:
            qury_temp.append('UNSEEN')
        if read_only and unread_only == False:
            qury_temp.append('SEEN')
        if not qury_temp:
            qury_temp.append('ALL')

        self.imap.select_folder(folder)
        qury = []
        for i in qury_temp:
            if isinstance(i, str):
                qury.append(bytes(i, 'utf-8'))
            else:
                qury.append(i)
        result = self.imap.search(qury)
        return result
    
    def fetch(self, msg_ids, folder: str = 'INBOX'):
        self.imap.select_folder(folder)
        result = self.imap.fetch(msg_ids, ['BODY[]', 'FLAGS', 'ENVELOPE', 'RFC822.SIZE'])
        data = {}
        for msg_id, msg in result.items():
            mail = email.message_from_bytes(msg[b'BODY[]'])
            info = {}
            if mail.is_multipart():
                for part in mail.walk():
                    part_type = part.get_content_type()
                    part_filename = part.get_filename()
                    print(part_type, part_filename)
                    if part_filename:
                        print(dir(part))
                    if part_type == 'text/plain':
                        info['text'] = part.get_payload(decode=True).decode(part.get_content_charset())
                    elif part_type == 'text/html':
                        info['html'] = part.get_payload(decode=True).decode(part.get_content_charset())
            else:
                info['text'] = mail.get_payload(decode=True).decode(mail.get_content_charset())
            data[msg_id] = info
        return data