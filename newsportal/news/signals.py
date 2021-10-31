from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mass_mail
from .models import Post


@receiver(post_save, sender=Post)
def notify_subscribers_publication(sender, instance, created, **kwargs):
    if created:
        subject = f'{instance.user_name} {instance.date.strftime("%d %m %Y")}'
    else:
        subject = f'Appointment changed for {instance.user_name} {instance.date.strftime("%d %m %Y")}'

    send_mass_mail(
        subject=subject,
        message=instance.message,
    )