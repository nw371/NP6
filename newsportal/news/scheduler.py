from django.utils.datetime_safe import datetime

# from newsportal.news.models import Category



def collect_weekly_articles():
    day_to_filter = datetime.day
    print(day_to_filter)

    #Category.objects.filter(date__gt = 90.0).values("name")