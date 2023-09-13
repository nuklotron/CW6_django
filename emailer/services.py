import smtplib

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail

from emailer.models import MailingLog, Client


def send_email(*args):

    for k in args:
        subject = k['mess'][0]['subject']
        message = k['mess'][0]['mail']
        client = k['client']
        email = k['email']
        subscription = k['subscription']

        try:
            send_status = send_mail(
                recipient_list=[email],
                subject=f"{subject}",
                message=f"{message}",
                from_email=settings.EMAIL_HOST_USER,
                fail_silently=False
            )

            if send_status == 1:
                print('Was sent to - ', email)
                status = MailingLog.STATUS_OK
                new_log = MailingLog.objects.create(status=status, client=client, subscription=subscription)
                new_log.save()

            else:
                print('FAILED to send - ', email)
                status = MailingLog.STATUS_FAILED
                new_log = MailingLog.objects.create(status=status, client=client, subscription=subscription)
                new_log.save()

        except smtplib.SMTPException as err:
            print('ERROR - ',  err, err.strerror)
            status = MailingLog.STATUS_FAILED
            new_log = MailingLog.objects.create(status=status, client=client, subscription=subscription)
            new_log.save()


def get_cached_details_for_client():
    if settings.CACHE_ENABLED:
        key = 'client_list'
        client_list = cache.get(key)
        if client_list is None:
            client_list = Client.objects.all()
            cache.set(key, client_list)
    else:
        client_list = Client.objects.all()
    return client_list
