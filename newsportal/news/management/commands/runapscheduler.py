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


    #arts = Post.objects.filter(date__lte = date_to_filter).values("name")
    # Subscriber.objects.filter(category=1).values('user__email')
    for i in range(1,4):
        arts = Category.objects.filter(id=i, post__date__gte = date_to_filter).values("post__name", "post__id")
        wkly_updates = render_to_string('email/weekly_pubs.html', {'posts': arts })
        #выдираем названия статей категории 1 созданных/изменённых за последнюю неделю
        print(arts)
        print(wkly_updates)
        filtered_susbscrbrs = list(CategorySub.objects.filter(category_id=i).values('subscriber_id__user__email'))
        print(f"FILTERED SUBS IN:  {i} CATEGORY: {filtered_susbscrbrs}")
        list_of_subscribers = [d['user__email'] for d in filtered_susbscrbrs if 'user__email' in d]
        print(f'THIS IS LIST OF EMAILS EMAIL SUPPOUSED TO BE SENT: {list_of_subscribers}')
        # отправляем письмо
        msg = EmailMultiAlternatives(
            subject=subject,
            from_email=admail,  # здесь указываете почту, с которой будете отправлять
            to=list_of_subscribers,  # здесь список получателей.
        )
        msg.attach_alternative(wkly_updates, "text/html")
        msg.content_subtype = "html"
        print("BODY: ", msg.body)
        print("MESSAGE : ", msg.message())
        msg.send()


    # cat_id = list(PostCategory.objects.filter(post_id=instance.id).values('category_id'))[0].get('category_id')
    # # print('EXTRACTED', cat_id)
    # # print("SUBS LIST", Subscriber.objects.filter())
    # filtered_susbscrbrs = list(CategorySub.objects.filter(category_id=cat_id).values('subscriber_id__user__email'))
    # # print('FILTERED SUBSCRIBERS', filtered_susbscrbrs)
    # # list_of_dictcs= list(Subscriber.objects.filter(category=1).values('user__email'))
    # list_of_subscribers = [d['user__email'] for d in filtered_susbscrbrs if 'user__email' in d]
    # print("THIS IS INSTANCE: ", instance)
    #
    # pub_updates = render_to_string('email/pub_updates.html', {'post': instance, 'instance': instance.id})
    # print("STRING_THE: ", pub_updates)
    # # отправляем письмо
    # msg = EmailMultiAlternatives(
    #     subject=subject,
    #     # body=f'Уважаемый подписчик, в интересующих Вас категориях произошли изменения. Можете перейти по ссылке http://127.0.0.1:8000/news/{instance.id}',  # сообщение с кратким описанием
    #     from_email=admail,  # здесь указываете почту, с которой будете отправлять
    #     to=list_of_subscribers,  # здесь список получателей. Например, секретарь, сам врач и т. д.
    # )
    # msg.attach_alternative(pub_updates, "text/html")
    # msg.content_subtype = "html"
    # print("BODY: ", msg.body)
    # print("MESSAGE : ", msg.message())
    # msg.send()

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
            trigger=CronTrigger(minute="*/3"),
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