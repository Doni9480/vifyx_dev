from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Referral
from constance import config
from users.models import User


@receiver(post_save, sender=Referral)
def compare_fields(sender, instance, **kwargs):
    if hasattr(instance, "old__tasks_completed"):
        if instance.tasks_completed > instance.old__tasks_completed:
            user = User.objects.filter(referral_code=instance.code).first()
            user.scores += config.POINT_INVITATION_BY_REFERRAL_LINK
            user.save()
