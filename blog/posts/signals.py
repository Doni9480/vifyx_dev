from django.utils.timezone import now
from django.db.models.signals import post_save
from django.dispatch import receiver
from posts.models import Post
from campaign.models import UserTaskChecking


@receiver(post_save, sender=Post)
def content_create_post(sender, instance, created, **kwargs):
    if created:
        obj_set = UserTaskChecking.objects.filter(user=instance.user, is_completed=False)
        if len(obj_set) == 1:
            obj_set[0].end_date = now()
            obj_set[0].is_completed = True
            obj_set[0].save()
