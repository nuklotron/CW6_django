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


def get_cached_details_for_client(client_pk):
    if settings.CACHE_ENABLED:
        key = f'details_list_{client_pk}'
        detail_list = cache.get(key)
        if detail_list is None:
            detail_list = Client.objects.filter(pk=client_pk)
            cache.set(key, detail_list)

    else:
        detail_list = Client.objects.filter(pk=client_pk)

    return detail_list
