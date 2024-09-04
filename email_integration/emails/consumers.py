import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import EmailAccount, EmailMessage
import imaplib
import email
import base64
from django.core.files.storage import default_storage


class EmailConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.account = None
        self.account_id = None

    async def connect(self):
        self.account_id = self.scope['url_route']['kwargs']['account_id']
        self.account = EmailAccount.objects.get(id=self.account_id)
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        command = json.loads(text_data)['command']
        if command == 'start':
            await self.fetch_emails()

    async def fetch_emails(self):
        await self.send(text_data=json.dumps({'status': 'fetching'}))

        try:
            imap = imaplib.IMAP4_SSL('imap.mail.ru', 993)
            imap.login(self.account.email, self.account.password)
            imap.select('inbox')

            _, data = imap.search(None, 'ALL')
            total_messages = len(data[0].split())

            for num in range(total_messages, 0, -1):
                _, data = imap.fetch(num, '(RFC822)')
                raw_email = data[0][1]
                email_message = email.message_from_bytes(raw_email)

                subject = email.header.decode_header(email_message['Subject'])[0][0].decode('utf-8') if isinstance(
                    email.header.decode_header(email_message['Subject'])[0][0], bytes) else \
                email.header.decode_header(email_message['Subject'])[0][0]
                sent_date = email.utils.parsedate_to_datetime(email_message['Date'])
                content = ''
                attachments = []

                if email_message.is_multipart():
                    for part in email_message.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get('Content-Disposition'))

                        try:
                            body = part.get_payload(decode=True).decode('utf-8')
                            if content_type == 'text/plain':
                                content += body
                        except:
                            pass

                        if content_disposition and 'attachment' in content_disposition:
                            filename = content_disposition.split(';')[1].split('=')[1]
                            attachment_data = part.get_payload(decode=True)
                            attachments.append({
                                'filename': filename,
                                'content': attachment_data
                            })

                else:
                    content = email_message.get_payload(decode=True).decode('utf-8')

                # Сохранение сообщения в базу данных
                message = EmailMessage.objects.create(
                    account=self.account,
                    subject=subject,
                    sent_date=sent_date,
                    received_date=datetime.now(),
                    content=content,
                    attachments=json.dumps(attachments)
                )

                # Сохранение прикрепленных файлов
                for attachment in attachments:
                    filename = attachment['filename']
                    path = f'emails/{self.account.email}/{message.id}/{filename}'
                    default_storage.save(path, ContentFile(attachment['content']))

                await self.send(text_data=json.dumps({
                    'status': 'processing',
                    'message': {
                        'id': message.id,
                        'subject': subject,
                        'sent_date': sent_date.isoformat(),
                        'received_date': datetime.now().isoformat(),
                        'content': content[:100] + '...' if len(content) > 100 else content,
                        'attachments': attachments
                    },
                    'progress': total_messages - num + 1,
                    'total': total_messages
                }))

            imap.close()
            imap.logout()

        except Exception as e:
            await self.send(text_data=json.dumps({'status': 'error', 'message': str(e)}))
        finally:
            await self.send(text_data=json.dumps({'status': 'completed'}))
