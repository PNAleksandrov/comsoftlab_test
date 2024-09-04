from __future__ import annotations

from django.contrib import admin

from .models import EmailMessage, EmailAccount

@admin.register(EmailMessage)
class EmailMessageAdmin(admin.ModelAdmin):
    pass

@admin.register(EmailAccount)
class EmailAccountAdmin(admin.ModelAdmin):
    pass