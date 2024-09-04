from django.db import models
from django.contrib.auth.models import User

class EmailAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.email

class EmailMessage(models.Model):
    account = models.ForeignKey(EmailAccount, on_delete=models.CASCADE, null=True)
    subject = models.CharField(max_length=255)
    sent_date = models.DateTimeField()
    received_date = models.DateTimeField(auto_now=True)
    content = models.TextField()
    attachments = models.JSONField(default=list, null=True)

    def get_attachment(self, index):
        if index < len(self.attachments):
            attachment = self.attachments[index]
            path = f'emails/{self.account.email}/{self.id}/{attachment["filename"]}'
            return default_storage.open(path).read()
        return None
