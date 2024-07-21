from typing import Iterable
from django.db import models
from django.conf import settings
from django.template.defaultfilters import slugify as default_slugify
from transliterate import slugify
from django.contrib.auth.models import User


class Campaign(models.Model):
    name = models.CharField(max_length=60)
    slug = models.SlugField(max_length=50, unique=True, null=True)
    description = models.TextField()
    prize_fund = models.IntegerField()
    image = models.ImageField(upload_to="campaign_images/", blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            slug_name = default_slugify(self.name) 
            if not slug_name:
                slug_name = slugify(self.name)
            self.slug = slug_name
        super(Campaign, self).save(*args, **kwargs)


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
        ("referral_registration", "Referral Registration"),
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
    content_usage_type = models.CharField(max_length=50, choices=CONTENT_USAGE, blank=True, null=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    points_reward = models.IntegerField()
    deadline = models.DateField(null=True, blank=True)
    total_pool_points = models.IntegerField(null=True, blank=True)
    external_link = models.URLField(blank=True)


class UserTaskChecking(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, verbose_name="Task")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="User"
    )
    is_completed = models.BooleanField(default=False, verbose_name="Is completed")
    points_awarded = models.IntegerField(default=0, verbose_name="Points")
    start_date = models.DateTimeField(auto_now_add=True, verbose_name="Start date")
    end_date = models.DateTimeField(null=True, blank=True, verbose_name="End date")
    
    
    def save(self, *args, **kwargs) -> None:
        if self.is_completed:
            task_owner_scores = self.task.campaign.user.scores
            if task_owner_scores >= self.points_awarded:
                self.task.campaign.user.scores = task_owner_scores - self.points_awarded
                self.task.campaign.user.save()
                
                total_points = self.user.scores
                self.user.scores = total_points + self.points_awarded
                self.user.save()
        return super().save(*args, **kwargs)
