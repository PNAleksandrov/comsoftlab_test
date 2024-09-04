from django.urls import path

from .views import email_list, email_consumer

urlpatterns = [
    path('emails/', email_list, name='emails'),
    path('consumer/<int:account_id>/', email_consumer, name='email_consumer'),
]