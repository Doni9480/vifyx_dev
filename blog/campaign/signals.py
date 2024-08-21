from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils.timezone import now
from referrals.models import Referral
from transactions.models import Transactions
from .models import UserTaskChecking
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

    if hasattr(instance, "old__is_received"):
        if instance.is_completed and not instance.old__is_received and not instance.is_received:
            if instance.task.system_source_company_remuneration():
                Transactions.create_translation_for_completing_tasks(
                    from_user=Transactions.get_or_create_system_user_object(),
                    to_user=instance.user,
                    amount=instance.points_awarded,
                    task_checking_obj=instance,
                )
            else:
                Transactions.create_translation_for_completing_tasks(
                    from_user=instance.task.campaign.user,
                    to_user=instance.user,
                    amount=instance.points_awarded,
                    task_checking_obj=instance,
                )
        elif instance.is_completed and not instance.old__is_received and instance.is_received:
            Transactions.update_translation_for_completing_tasks(task_checking_obj=instance)
            instance.received_data = now()
            instance.save()
