from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import Post, PostCategory, CategorySub
from .secda import admail

@receiver(post_save, sender=Post)
def notify_subscribers_publication(instance, created, **kwargs):
    if not created:
        subject = f'Изменена публикация: {instance.name} {instance.date.strftime("%d %m %Y")}'
        cat_id = list(PostCategory.objects.filter(post_id=instance.id).values('category_id'))[0].get('category_id')
        filtered_susbscrbrs = list(CategorySub.objects.filter(category_id=cat_id).values('subscriber_id__user__email'))
        list_of_subscribers = [d['subscriber_id__user__email'] for d in filtered_susbscrbrs if 'subscriber_id__user__email' in d]
        pub_updates = render_to_string('email/pub_updates.html', {'post': instance, 'instance': instance.id})
        send_updates(subject, pub_updates, list_of_subscribers)

@receiver(m2m_changed, sender=Post.category.through)
def notify_subscribers_publication(instance, **kwargs):
    subject = f'Добавлена публикация: {instance.name} {instance.date.strftime("%d %m %Y")}'
    print(f"_____________________________________________________________INSTANCE AND KWARGS: {instance} **** {kwargs}")
    cat_id = list(kwargs.get('pk_set'))[0]
    filtered_susbscrbrs = list(CategorySub.objects.filter(category_id=cat_id).values('subscriber_id__user__email'))
    print(f"_____________________________________________________________FILTERED SUBSCIRBERS: {filtered_susbscrbrs}")
    list_of_subscribers = [d['subscriber_id__user__email'] for d in filtered_susbscrbrs if 'subscriber_id__user__email' in d]
    pub_updates = render_to_string('email/pub_updates.html', {'post': instance, 'instance': instance.id})
    send_updates(subject, pub_updates, list_of_subscribers)
    print(f"_____________________________________________________________LIST OF SUBSCIRBERS: {list_of_subscribers}")


def send_updates(subject, pub_updates, list_of_subscribers):
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



