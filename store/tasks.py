from celery import shared_task
# from django.core.mail import send_mail
from time import sleep

from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string


@shared_task
def send_email_task(user_name, user_email, items):
    sleep(10)
    context = {'name': user_name, 'items': items}
    template = render_to_string('store/email_template.html', context)
    email = EmailMessage('Order Confirmation Mail',
                         template,
                         settings.EMAIL_HOST_USER,
                         [user_email],
                         )
    email.fail_silently = False
    email.send()
    return None
