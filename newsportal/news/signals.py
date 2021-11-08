from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from .models import Post, Subscriber
from .secda import admail


@receiver(post_save, sender=Post)
def notify_subscribers_publication(sender, instance, created, **kwargs):
    if created:
        subject = f'Добавлена публикация: {instance.name} {instance.date.strftime("%d %m %Y")}'
    else:
        subject = f'Изменена публикация: {instance.name} {instance.date.strftime("%d %m %Y")}'

    list_of_dictcs= list(Subscriber.objects.filter(category=1).values('user__email'))
    list_of_subscribers = [d['user__email'] for d in list_of_dictcs if 'user__email' in d]
    print(list_of_subscribers)

    # отправляем письмо
    msg = EmailMultiAlternatives(
        subject=subject,
        body=f'Уважаемый подписчик, в интересующих Вас категориях произошли изменения',  # сообщение с кратким описанием
        from_email=admail,  # здесь указываете почту, с которой будете отправлять
        to=list_of_subscribers, # здесь список получателей. Например, секретарь, сам врач и т. д.
    )
    msg.send()