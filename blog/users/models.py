import binascii
import os

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError

from apscheduler.schedulers.background import BackgroundScheduler


class User(AbstractUser):
    email = models.EmailField(verbose_name="email address", unique=True)
    first_name = models.CharField(max_length=255, verbose_name="First name", blank=False, null=False)
    scores = models.IntegerField(verbose_name="scores", default=0)
    language = models.CharField(max_length=255, verbose_name="Language", default="any")
    unearned_scores = models.IntegerField(verbose_name="unearned scores", default=0)
    is_published_post = models.BooleanField(default=True)
    is_published_comment = models.BooleanField(default=True)
    is_notificated = models.BooleanField(default=True, verbose_name="Is notificated")
    is_autorenewal = models.BooleanField(default=True, verbose_name="Is auto renewal")
    twitter = models.CharField(max_length=255, null=True, blank=True, verbose_name="Twitter")
    telegram_wallet = models.CharField(max_length=255, null=True, blank=True, verbose_name="Telegram wallet")

    REQUIRED_FIELDS = ["last_name"]

    class Meta:
        db_table = "user"
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return self.username


class Token(models.Model):
    key = models.CharField(
        verbose_name="Key", max_length=255, primary_key=True, unique=True
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created = models.DateTimeField(verbose_name="Created", auto_now_add=True)

    def __str__(self):
        return self.key

    @classmethod
    def generate_key(cls):
        return binascii.hexlify(os.urandom(40)).decode()
    

def validate_only_one_instance(obj):
    model = obj.__class__
    if model.objects.count() > 0 and obj.id != model.objects.get().id:
        raise ValidationError("Can only create 1 %s instance" % model.__name__)


class TotalScore(models.Model):
    scores = models.IntegerField(verbose_name="scores")
    hour = models.IntegerField(verbose_name="hour", default=0)
    minute = models.IntegerField(verbose_name="minute", default=0)

    def clean(self):
        validate_only_one_instance(self)

    def get_hour(self):
        return self.hour

    def get_minute(self):
        return self.minute


class Percent(models.Model):
    percent = models.IntegerField(verbose_name="percent", default=30)

    def clean(self):
        validate_only_one_instance(self)
        

class Hide(models.Model):
    hider = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="hider"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )


@receiver(post_save, sender=User)
def create_scores(sender, **kwargs):
    if TotalScore.objects.all().count() == 0:
        TotalScore.objects.create(scores=0)


@receiver(post_save, sender=User)
def create_percent(sender, **kwargs):
    if Percent.objects.all().count() == 0:
        Percent.objects.create()


def send_scores():
    users = User.objects.all()
    if users:
        _total_scores = TotalScore.objects.all()
        if _total_scores:
            scores = _total_scores[0].scores
            for user in users:
                user.unearned_scores = scores
                user.save()


@receiver(post_save, sender=TotalScore)
def change_time_to_scores(sender, **kwargs):
    scheduler = BackgroundScheduler()
    total_score = TotalScore.objects.all()[0]
    if scheduler.get_job(job_id="send_scores"):

        scheduler.remove_job(job_id="send_scores")
    scheduler.add_job(
        send_scores,
        "cron",
        hour=total_score.hour,
        minute=total_score.minute,
        id="send_scores",
    )
    scheduler.start()
