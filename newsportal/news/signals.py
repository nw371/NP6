from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .models import Post, Subscriber, Category, PostCategory, CategorySub
from .secda import admail


@receiver(post_save, sender=Post)
def notify_subscribers_publication(sender, instance, created, **kwargs):
    if created:
        subject = f'Добавлена публикация: {instance.name} {instance.date.strftime("%d %m %Y")}'
    else:
        subject = f'Изменена публикация: {instance.name} {instance.date.strftime("%d %m %Y")}'

    # print("INSTANCE CATEGROY",PostCategory.objects.filter(post_id=instance.id).values('category_id'))

    cat_id = list(PostCategory.objects.filter(post_id=instance.id).values('category_id'))[0].get('category_id')
    # print('EXTRACTED', cat_id)
    # print("SUBS LIST", Subscriber.objects.filter())
    filtered_susbscrbrs = list(CategorySub.objects.filter(category_id=cat_id).values('subscriber_id__user__email'))
    # print('FILTERED SUBSCRIBERS', filtered_susbscrbrs)
    # list_of_dictcs= list(Subscriber.objects.filter(category=1).values('user__email'))
    list_of_subscribers = [d['user__email'] for d in filtered_susbscrbrs if 'user__email' in d]
    print("THIS IS INSTANCE: ",instance)

    pub_updates = render_to_string('email/pub_updates.html', {'post': instance, 'instance': instance.id})
    print("STRING_THE: ",pub_updates)
    # отправляем письмо
    msg = EmailMultiAlternatives(
        subject=subject,
        # body=f'Уважаемый подписчик, в интересующих Вас категориях произошли изменения. Можете перейти по ссылке http://127.0.0.1:8000/news/{instance.id}',  # сообщение с кратким описанием
        from_email=admail,  # здесь указываете почту, с которой будете отправлять
        to=list_of_subscribers, # здесь список получателей. Например, секретарь, сам врач и т. д.
    )
    msg.attach_alternative(pub_updates, "text/html")
    msg.content_subtype = "html"
    print("BODY: ", msg.body)
    print("MESSAGE : ", msg.message())
    msg.send()
    #LoTp78rN6zVwptLy