# runapscheduler.py
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from django.conf import settings
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util
from django.core.management import BaseCommand

from emailer.views import send_mails

logger = logging.getLogger(__name__)


@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """
    This job deletes APScheduler job execution entries older than `max_age` from the database.
    It helps to prevent the database from filling up with old historical records that are no
    longer useful.

    :param max_age: The maximum length of time to retain historical job execution records.
                    Defaults to 7 days.
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        print('Service is started')
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        try:
            print('Starting scheduler...')
            logger.info("Starting scheduler...")
            scheduler.add_job(send_mails, 'interval', seconds=60, args='1')
            scheduler.start()
        except KeyboardInterrupt:
            print('Stopping scheduler...')
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            print("Scheduler shut down successfully!")
            logger.info("Scheduler shut down successfully!")
