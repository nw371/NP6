import datetime
import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from news.models import Category, Post #pycharm хреново работает с путями в django поектах. этот импорт, хоть и подчёркнут. но работает

from news.models import CategorySub
from news.secda import admail

logger = logging.getLogger(__name__)

def collect_weekly_articles():
    date_to_filter = datetime.date.today()-datetime.timedelta(days=7)
    print(date_to_filter)
    subject = "Обновления статей за неделю"

    for i in range(1,4):
        arts = Category.objects.filter(id=i, post__date__gte = date_to_filter).values("post__name", "post__id")
        wkly_updates = render_to_string('email/weekly_pubs.html', {'posts': arts })
        #выдираем названия статей категории 1 созданных/изменённых за последнюю неделю
        filtered_susbscrbrs = list(CategorySub.objects.filter(category_id=i).values('subscriber_id__user__email'))
        list_of_subscribers = [d['subscriber_id__user__email'] for d in filtered_susbscrbrs if 'subscriber_id__user__email' in d]
        # отправляем письмо
        msg = EmailMultiAlternatives(
            subject=subject,
            from_email=admail,  # здесь указываете почту, с которой будете отправлять
            to=list_of_subscribers,  # здесь список получателей.
        )
        msg.attach_alternative(wkly_updates, "text/html")
        msg.content_subtype = "html"
        msg.send()


# наша задача по выводу текста на экран
def my_job():
    #  Your job processing logic here...
    print('hello from job')
    collect_weekly_articles()


# функция, которая будет удалять неактуальные задачи
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # добавляем работу нашему задачнику
        scheduler.add_job(
            my_job,
            trigger=CronTrigger(day_of_week="6"),
            # То же, что и интервал, но задача тригера таким образом более понятна django
            id="my_job",  # уникальный айди
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить, либо уже выполнять не надо.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")