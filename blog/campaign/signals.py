from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils.timezone import now
from referrals.models import Referral
from .models import UserTaskChecking
from constance import config
from users.models import User


@receiver(post_save, sender=UserTaskChecking)
def compare_fields(sender, instance, **kwargs):
    if hasattr(instance, "old__is_completed"):
        if instance.old__is_completed == False and instance.is_completed == True:
            instance.end_date = now()
            user_referral = Referral.objects.filter(referral_user=instance.user.pk)
            if len(user_referral):
                referral = user_referral.first()
                referral.tasks_completed += 1
                referral.save()
                
    if instance.task.campaign.reward_source == "owner":
        if instance.is_received and instance.received_data is None:
            instance.received_data = now()
            task_owner_scores = instance.task.campaign.user.scores
            campaign_owner_scores = instance.task.campaign.prize_fund
            if (
                task_owner_scores >= instance.points_awarded
                and task_owner_scores >= campaign_owner_scores
            ):
                instance.task.campaign.user.scores = (
                    task_owner_scores - instance.points_awarded
                )
                instance.task.campaign.user.save()

                instance.task.campaign.prize_fund = (
                    campaign_owner_scores - instance.points_awarded
                )
                instance.task.campaign.save()

                total_points = instance.user.scores
                instance.user.scores = total_points + instance.points_awarded
                instance.user.save()
        if instance.task.campaign.reward_source == "endless":
            if instance.is_received and instance.received_data is None:
                instance.received_data = now()
                total_points = instance.user.scores
                instance.user.scores = total_points + instance.points_awarded
                instance.user.save()
