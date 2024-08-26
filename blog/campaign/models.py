from django.utils.timezone import now
from typing import Iterable
from django.db import models
from django.db.models import Count
from django.conf import settings
from django.template.defaultfilters import slugify as default_slugify
from transliterate import slugify
from django.core.exceptions import ValidationError
from users.models import User


class Campaign(models.Model):
    REWARD_SOURCE_CHOICES = (
        ("owner", "Владелец компании"),
        ("endless", "Бесконечный"),
    )
    name = models.CharField(max_length=60)
    slug = models.SlugField(max_length=50, unique=True, null=True)
    description = models.TextField()
    prize_fund = models.IntegerField(null=True, blank=True)
    image = models.ImageField(upload_to="campaign_images/", blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name="is active")
    reward_source = models.CharField(
        max_length=50,
        choices=REWARD_SOURCE_CHOICES,
        default="owner",
        verbose_name="Источник награды кампании",
    )

    def __str__(self):
        return self.name

    def system_source_of_reward(self):
        return self.reward_source == "endless"

    def save(self, *args, **kwargs):
        if not self.slug:
            slug_name = default_slugify(self.name)
            if not slug_name:
                slug_name = slugify(self.name)
            self.slug = slug_name
        super(Campaign, self).save(*args, **kwargs)


class SubscriptionsCampaign(models.Model):
    user = models.OneToOneField(
        User, related_name="subscriptions_campaigns", on_delete=models.CASCADE
    )
    campaigns = models.ManyToManyField(
        Campaign,
        verbose_name="Campaign",
    )

    def __str__(self):
        return f"{self.user.username} - Subscriptions Campaigns"

    class Meta:
        verbose_name = "Subscriptions Campaigns"
        verbose_name_plural = "Subscriptions Campaigns"
        


class Task(models.Model):
    TYPES = (
        ("telegram_subscription", "Telegram Subscription"),
        ("twitter_subscription", "Twitter Subscription"),
        ("website_visit", "Website Visit"),
        ("content_creation", "Content Creation"),
        ("content_usage", "Content Usage"),
        ("comment", "Comment"),
        ("wallet_connect", "Wallet Connect"),
        ("twitter_connect", "Twitter Connect"),
        ("periodic_bonus", "Periodic Bonus"),
    )
    CONTENT_USAGE = (
        ("test", "Test"),
        ("quest", "Quest"),
        ("post", "Post"),
        ("survey", "Survey"),
        ("comment", "Comment"),
    )
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    task_type = models.CharField(max_length=50, choices=TYPES)
    content_usage_type = models.CharField(
        max_length=50, choices=CONTENT_USAGE, blank=True, null=True
    )
    name = models.CharField(max_length=100)
    description = models.TextField()
    points_reward = models.IntegerField()
    deadline = models.DateField(null=True, blank=True)
    total_pool_points = models.IntegerField(null=True, blank=True)
    external_link = models.URLField(null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name="is active")
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.name

    def system_source_company_remuneration(self):
        return self.campaign.system_source_of_reward()


class UserTaskChecking(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name="Task")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="User"
    )
    is_completed = models.BooleanField(default=False, verbose_name="Is completed")
    points_awarded = models.IntegerField(default=0, verbose_name="Points")
    start_date = models.DateTimeField(auto_now_add=True, verbose_name="Start date")
    end_date = models.DateTimeField(null=True, blank=True, verbose_name="End date")
    is_received = models.BooleanField(default=False, verbose_name="Is received")
    received_data = models.DateTimeField(
        null=True, blank=True, verbose_name="Received data"
    )

    def __str__(self):
        return f"{self.user.username} - {self.task.name}"

    @staticmethod
    def getting_statistics(campaign_id):
        campaign_obj = Campaign.objects.get(id=campaign_id)
        queryset = UserTaskChecking.objects.all()
        lids = (
            User.objects.annotate(completed_tasks_count=Count("usertaskchecking"))
            .values("completed_tasks_count", "username")
            .filter(completed_tasks_count__gt=0)
            .order_by("completed_tasks_count")[:10]
        )
        statistics = {
            "lids": lids,
            "number_of_participants": queryset.distinct("user").count(),
            "total_completed_tasks": queryset.filter(
                task__campaign__pk=campaign_id
            ).count(),
            "remaining_points": campaign_obj.prize_fund,
        }
        return statistics

    def save(self, *args, **kwargs) -> None:
        if self.pk:
            old_instance = UserTaskChecking.objects.get(pk=self.pk)
            self.old__is_completed = old_instance.is_completed
            self.old__is_received = old_instance.is_received
            self.old__end_date = old_instance.end_date

        return super().save(*args, **kwargs)
