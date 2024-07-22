from django.utils.timezone import now
from django.db.models.signals import post_save
from django.dispatch import receiver
from quests.models import Quest
from campaign.models import UserTaskChecking


@receiver(post_save, sender=Quest)
def content_create_comment(sender, instance, created, **kwargs):
    if created:
        obj_set = UserTaskChecking.objects.filter(user=instance.user, is_completed=False)
        if len(obj_set) == 1:
            obj_set[0].end_date = now()
            obj_set[0].is_completed = True
            obj_set[0].save()
