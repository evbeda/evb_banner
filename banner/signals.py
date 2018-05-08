from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from banner.models import Banner
from .utils import create_webhook


@receiver(post_save, sender=Banner)
def create_user_webhook(sender, instance, **kwargs):
    User = get_user_model()
    user = User.objects.get(banner=instance)
    create_webhook(user)
