from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Referral, BonusCoefficients
from constance import config
from users.models import User


@receiver(post_save, sender=Referral)
def compare_fields(sender, instance, **kwargs):
    if hasattr(instance, "old__tasks_completed"):
        if instance.old__tasks_completed == 0 and instance.tasks_completed > instance.old__tasks_completed:
            user = User.objects.filter(referral_code=instance.code).first()
            ref_user_count = user.referred_set.filter(tasks_completed__gt=0).count()
            bonus_coefficient = BonusCoefficients.get_coefficient(ref_user_count)
            user.scores += int(config.POINT_INVITATION_BY_REFERRAL_LINK * bonus_coefficient)
            user.save()
