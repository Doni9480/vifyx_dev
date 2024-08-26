from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from transactions.models import Transactions
from .models import Referral, BonusCoefficients
from configs.models import SiteConfiguration
from users.models import User


@receiver(post_save, sender=Referral)
def compare_fields(sender, instance, **kwargs):
    if hasattr(instance, "old__tasks_completed"):
        if (
            instance.old__tasks_completed == 0
            and instance.tasks_completed > instance.old__tasks_completed
        ):
            user = User.objects.filter(referral_code=instance.code).first()
            ref_user_count = user.referred_set.filter(tasks_completed__gt=0).count()
            # if 
            bonus_coefficient = BonusCoefficients.get_coefficient(ref_user_count)
            config = SiteConfiguration.get_solo()
            first_task = instance.first_task_user()
            if first_task and first_task.system_source_company_remuneration():
                scores = int(config.point_for_first_task * bonus_coefficient)
            else:
                scores = int(config.point_invitation_by_referral_link)
            Transactions.create_system_transaction(
                user=user,
                amount=scores,
                info={
                    "type": "referral",
                    "pk": instance.pk,
                    "title": "New user",
                    "description": f"A new user has been registered: {instance.referral_user.username}",
                },
            )
