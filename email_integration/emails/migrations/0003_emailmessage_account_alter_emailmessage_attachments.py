# Generated by Django 5.1 on 2024-09-02 17:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emails', '0002_alter_emailmessage_received_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailmessage',
            name='account',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='emails.emailaccount'),
        ),
        migrations.AlterField(
            model_name='emailmessage',
            name='attachments',
            field=models.JSONField(default=list, null=True),
        ),
    ]
