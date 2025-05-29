from .utils     import try_for, safecode, flatten
from .data      import EmailEndpoint, EmailRecvContent, EmailAttachment
from imapclient import IMAPClient
from rich       import print
from typing     import List
import datetime
import email
import smtplib
import os
from email.mime.text      import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base      import MIMEBase
from email                import encoders
from email.mime.image     import MIMEImage
from email.header        import decode_header


class EmailService:
    def __init__(self, endpoint: EmailEndpoint):
        """
        Args:
            endpoint (EmailEndpoint): 邮箱服务端点配置
        """
        self.endpoint = endpoint
        self.imap: IMAPClient = None
        self.smtp: smtplib.SMTP = None
        self._init_imap()
        self._init_smtp()
    
    def __del__(self):
        if self.imap:
            try: self.imap.logout()
            except: pass
        if self.smtp:
            try: self.smtp.quit()
            except: pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.__del__()

    def _init_imap(self):
        """
        初始化IMAP连接。
        Raises:
            Exception: 登录失败时抛出异常。
        """
        self.imap = IMAPClient(
            host=self.endpoint.imap,
            ssl=self.endpoint.ssl
        )
        try:
            self.imap.login(
                username=self.endpoint.account,
                password=self.endpoint.authorization
            )
        except Exception as e:
            print(f"[red]IMAP login failed for {self.endpoint.account}: {e}[/red]")
            raise

    def _init_smtp(self):
        """
        初始化SMTP连接。
        Raises:
            Exception: 登录失败时抛出异常。
        """
        if self.smtp is None:
            try:
                if self.endpoint.ssl:
                    self.smtp = smtplib.SMTP_SSL(self.endpoint.smtp, 465)
                else:
                    self.smtp = smtplib.SMTP(self.endpoint.smtp)
                self.smtp.login(self.endpoint.account, self.endpoint.authorization)
            except Exception as e:
                print(f"[red]SMTP login failed for {self.endpoint.account}: {e}[/red]")
                self.smtp = None
    
    def disconnect(self):
        """
        断开连接。
        """
        self.__del__()
    
    @property
    def folder(self):
        """
        获取所有邮箱文件夹及邮件数。
        Returns:
            list[dict]: 每个文件夹包含'name'和'count'。
        """
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
        flags: list = None,
        from_addr: str = None,
        to_addr: str = None,
        subject: str = None,
        body: str = None,
        custom_query: list = None,
        logic: str = 'AND',  # 'AND'/'OR'
    ):
        """
        高级搜索邮件。
        Args:
            folder (str): 文件夹名。
            since (str): 起始日期，格式YYYY-MM-DD。
            before (str): 截止日期，格式YYYY-MM-DD。
            unread_only (bool): 仅未读。
            read_only (bool): 仅已读。
            flags (list[str]|None): 附加IMAP标志（如['Flagged', 'Answered']）。
            from_addr (str|None): 发件人包含。
            to_addr (str|None): 收件人包含。
            subject (str|None): 主题包含。
            body (str|None): 正文包含。
            custom_query (list|None): 直接传递IMAP原生查询片段。
            logic (str): 条件组合方式，'AND'或'OR'。
        Returns:
            list: 匹配的邮件ID列表。
        """
        qury_temp = []
        if since:
            since = datetime.datetime.strptime(since, "%Y-%m-%d")
            qury_temp.extend(['SINCE', since])
        if before:
            before = datetime.datetime.strptime(before, "%Y-%m-%d")
            qury_temp.extend(['BEFORE', before])
        if unread_only and not read_only:
            qury_temp.append('UNSEEN')
        if read_only and not unread_only:
            qury_temp.append('SEEN')
        if flags:
            for flag in flags:
                if not flag.startswith('\\'):
                    flag = '\\' + flag
                qury_temp.append(flag.upper())
        if from_addr:
            qury_temp.extend(['FROM', from_addr])
        if to_addr:
            qury_temp.extend(['TO', to_addr])
        if subject:
            qury_temp.extend(['SUBJECT', subject])
        if body:
            qury_temp.extend(['BODY', body])
        if custom_query:
            # 允许用户直接传递IMAP原生查询片段
            qury_temp.extend(custom_query)
        # 逻辑组合
        if logic.upper() == 'OR' and len(qury_temp) > 1:
            # 只支持两两OR嵌套，IMAP协议限制
            while len(qury_temp) > 2:
                a = qury_temp.pop(0)
                b = qury_temp.pop(0)
                qury_temp.insert(0, ['OR', a, b])
            qury_temp = ['OR'] + qury_temp
        if not qury_temp:
            qury_temp.append('ALL')

        results = []
        if folder == '*':
            for f in [x['name'] for x in self.folder]:
                try:
                    ids = self.search(f, since, before, unread_only, read_only, flags, from_addr, to_addr, subject, body, custom_query, logic)
                    results.extend(ids)
                except Exception as e:
                    print(f"[yellow]搜索文件夹{f}失败: {e}[/yellow]")
            return results
        self.imap.select_folder(folder)
        qury = []
        for i in flatten(qury_temp):
            if isinstance(i, str):
                qury.append(bytes(i, 'utf-8'))
            else:
                qury.append(i)
        result = self.imap.search(qury)
        return result
    
    def fetch(self, msg_ids, folder: str = 'INBOX') -> List[EmailRecvContent]:
        """
        获取邮件内容。
        Args:
            msg_ids (list): 邮件ID列表。
            folder (str): 文件夹名，支持'*'递归所有文件夹。
        Returns:
            list[EmailRecvContent]: 邮件内容对象列表。
        """
        mails = []
        if folder == '*':
            for f in [x['name'] for x in self.folder]:
                try:
                    mails.extend(self.fetch(msg_ids, f))
                except Exception as e:
                    print(f"[yellow]抓取文件夹{f}失败: {e}[/yellow]")
            return mails
        self.imap.select_folder(folder)
        result = self.imap.fetch(msg_ids, ['BODY[]', 'FLAGS', 'ENVELOPE', 'RFC822.SIZE'])
        for msg_id, msg in result.items():
            mail = email.message_from_bytes(msg[b'BODY[]'])
            content = EmailRecvContent()
            content.email_id = msg_id
            # 头部解析
            def parse_addr(addr_str):
                name, addr = email.utils.parseaddr(addr_str or '')
                addr = addr.strip('<>') if addr else None
                return {"name": name, "addr": addr} if addr else None
            def parse_addr_list(addr_list):
                return [parse_addr(f"{n} <{a}>") for n, a in (email.utils.getaddresses(addr_list or [])) if a]
            def decode_mime_words(s):
                if not s:
                    return ''
                parts = decode_header(s)
                return ''.join([
                    (b.decode(enc or 'utf-8') if isinstance(b, bytes) else b)
                    for b, enc in parts
                ])
            content.subject = decode_mime_words(mail.get('Subject'))
            content.from_addr = parse_addr(mail.get('From'))
            if content.from_addr:
                content.from_addr['name'] = decode_mime_words(content.from_addr['name'])
            content.to_addrs = parse_addr_list(mail.get_all('To', []))
            for addr in content.to_addrs:
                addr['name'] = decode_mime_words(addr['name'])
            content.cc = parse_addr_list(mail.get_all('Cc', []))
            for addr in content.cc:
                addr['name'] = decode_mime_words(addr['name'])
            content.bcc = parse_addr_list(mail.get_all('Bcc', []))
            for addr in content.bcc:
                addr['name'] = decode_mime_words(addr['name'])
            content.reply_to = parse_addr(mail.get('Reply-To'))
            if content.reply_to:
                content.reply_to['name'] = decode_mime_words(content.reply_to['name'])
            # 日期格式化
            raw_date = mail.get('Date')
            parsed_date = None
            if raw_date:
                try:
                    from email.utils import parsedate_to_datetime
                    dt = parsedate_to_datetime(raw_date)
                    parsed_date = dt.strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    parsed_date = raw_date
            content.date = parsed_date
            content.message_id = mail.get('Message-ID')
            content.in_reply_to = mail.get('In-Reply-To')
            content.references = mail.get('References')
            content.attachments = []
            # flags
            content.flags = list(msg.get('FLAGS', []))
            # 正文和附件
            if mail.is_multipart():
                for part in mail.walk():
                    part_type = part.get_content_type()
                    part_filename = part.get_filename()
                    content_id = part.get('Content-ID')
                    is_inline = part.get('Content-Disposition', '').startswith('inline') or bool(content_id)
                    if part_filename or is_inline:
                        # 附件或内嵌资源
                        attachment = EmailAttachment(
                            filename=part_filename,
                            content_type=part_type,
                            content=part.get_payload(decode=True),
                            is_inline=is_inline,
                            cid=content_id.strip('<>') if content_id else None
                        )
                        content.attachments.append(attachment)
                    elif part_type == 'text/plain' and not content.text:
                        content.text = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', errors='replace')
                    elif part_type == 'text/html' and not content.html:
                        content.html = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', errors='replace')
            else:
                content.text = mail.get_payload(decode=True).decode(mail.get_content_charset() or 'utf-8', errors='replace')
            mails.append(content)
        return mails

    def send_mail(self, to_addrs, subject, body, subtype='plain', html_body=None, attachments=None, inline_images=None):
        """
        发送邮件，支持附件和内嵌图片（cid）。
        Args:
            to_addrs (str|list): 收件人。
            subject (str): 主题。
            body (str): 纯文本正文。
            subtype (str): 'plain'或'html'。
            html_body (str): HTML正文。
            attachments (str|list): 附件路径。
            inline_images (dict): {'cid': 'path/to/img'}，html_body中用<img src="cid:cid">引用。
        Returns:
            None
        """
        msg = MIMEMultipart('related') if (html_body or attachments or inline_images) else MIMEText(body, subtype, 'utf-8')
        msg['From'] = self.endpoint.account
        msg['To'] = to_addrs if isinstance(to_addrs, str) else ', '.join(to_addrs)
        msg['Subject'] = subject
        if html_body or attachments or inline_images:
            alt = MIMEMultipart('alternative')
            alt.attach(MIMEText(body, 'plain', 'utf-8'))
            if html_body:
                alt.attach(MIMEText(html_body, 'html', 'utf-8'))
            msg.attach(alt)
            # 附件处理
            if attachments:
                if isinstance(attachments, str):
                    attachments = [attachments]
                for file_path in attachments:
                    if not os.path.isfile(file_path):
                        print(f"[red]附件不存在: {file_path}[/red]")
                        continue
                    with open(file_path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(file_path)}"')
                        msg.attach(part)
            # 内嵌图片处理
            if inline_images:
                for cid, img_path in inline_images.items():
                    if not os.path.isfile(img_path):
                        print(f"[red]内嵌图片不存在: {img_path}[/red]")
                        continue
                    with open(img_path, 'rb') as img_f:
                        img = MIMEImage(img_f.read())
                        img.add_header('Content-ID', f'<{cid}>')
                        img.add_header('Content-Disposition', 'inline', filename=os.path.basename(img_path))
                        msg.attach(img)
        self.smtp.sendmail(self.endpoint.account, to_addrs, msg.as_string())
        print(f"[green]邮件已发送至 {to_addrs}[/green]")

    def set_flags(self, msg_ids, folder='INBOX', seen=None, flagged=None, flags_add=None, flags_remove=None):
        """
        更改邮件状态（如已读、未读、星标等），支持自定义IMAP标志。
        Args:
            msg_ids (list/int): 邮件ID或ID列表。
            folder (str): 邮件所在文件夹。
            seen (bool|None): 设为已读(True)、未读(False)或不变(None)。
            flagged (bool|None): 设为星标(True)、取消星标(False)或不变(None)。
            flags_add (list[str]|None): 需添加的IMAP标志（如['Answered', 'Draft']）。
            flags_remove (list[str]|None): 需移除的IMAP标志。
        Returns:
            None
        """
        self.imap.select_folder(folder)
        if not isinstance(msg_ids, (list, tuple)):
            msg_ids = [msg_ids]
        if seen is not None:
            if seen:
                self.imap.add_flags(msg_ids, [b'\\Seen'])
            else:
                self.imap.remove_flags(msg_ids, [b'\\Seen'])
        if flagged is not None:
            if flagged:
                self.imap.add_flags(msg_ids, [b'\\Flagged'])
            else:
                self.imap.remove_flags(msg_ids, [b'\\Flagged'])
        def norm_flag(flag):
            if not flag.startswith('\\'):
                flag = '\\' + flag
            return flag.encode() if isinstance(flag, str) else flag
        if flags_add:
            self.imap.add_flags(msg_ids, [norm_flag(f) for f in flags_add])
        if flags_remove:
            self.imap.remove_flags(msg_ids, [norm_flag(f) for f in flags_remove])
    