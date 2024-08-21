import binascii
import os

from django.db import models
from django.db import utils
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError

from posts.models import Category as Category_post, Subcategory as Subcategory_post
from surveys.models import Category as Category_survey, Subcategory as Subcategory_survey
from custom_tests.models import Category as Category_test, Subcategory as Subcategory_test
from quests.models import Category as Category_quest, Subcategory as Subcategory_quest
from albums.models import Category as Category_album, Subcategory as Subcategory_album

from apscheduler.schedulers.background import BackgroundScheduler


def gen_referral_code():
    """Generate a unique 16-character alphanumeric string."""
    # Generate a random 16-character alphanumeric string
    while True:
        code = binascii.hexlify(os.urandom(8)).decode()
        try:
            if User.objects.filter(referral_code=code).count() == 0:
                return str(code)
        except utils.ProgrammingError:
            return str(code)

class User(AbstractUser):
    email = models.EmailField(verbose_name="email address", null=True, unique=True)
    first_name = models.CharField(
        max_length=255, verbose_name="First name", blank=False, null=False
    )
    scores = models.IntegerField(verbose_name="scores", default=0)
    language = models.CharField(max_length=255, verbose_name="Language", default="any")
    unearned_scores = models.IntegerField(verbose_name="unearned scores", default=0)
    is_published_post = models.BooleanField(default=True)
    is_published_comment = models.BooleanField(default=True)
    is_notificated = models.BooleanField(default=True, verbose_name="Is notificated")
    is_autorenewal = models.BooleanField(default=True, verbose_name="Is auto renewal")
    twitter = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Twitter"
    )
    telegram_wallet = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Telegram wallet"
    )
    referral_code = models.CharField(
        unique=True,
        default=gen_referral_code,
        null=True,
        blank=True,
        verbose_name="Referral code",
    )
    posts_category = models.ForeignKey(to=Category_post, on_delete=models.CASCADE, null=True, blank=True)
    surveys_category = models.ForeignKey(to=Category_survey, on_delete=models.CASCADE, null=True, blank=True)
    quests_category = models.ForeignKey(to=Category_quest, on_delete=models.CASCADE, null=True, blank=True)
    tests_category = models.ForeignKey(to=Category_test, on_delete=models.CASCADE, null=True, blank=True)
    albums_category = models.ForeignKey(to=Category_album, on_delete=models.CASCADE, null=True, blank=True)
    activity_level = models.PositiveIntegerField(default=0, verbose_name="Activity level")

    REQUIRED_FIELDS = ["last_name"]

    class Meta:
        db_table = "user"
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return self.username
    
    def get_subscriptions_campaigns(self):
        subscriptions_campaigns = self.subscriptionscampaigns_set.all()
        return subscriptions_campaigns
    
    def number_of_completed_tasks(self):
        return self.usertaskchecking_set.count()
    
    def number_of_points_for_completed_tasks(self):
        total_points = 0
        for obj in self.usertaskchecking_set.filter(is_completed=True):
            total_points += obj.task.points_reward
        return total_points

    def save(self, *args, **kwargs) -> None:
        try:
            if not self.referral_code:
                self.referral_code = gen_referral_code()
        except Exception as _:
            print(_)
        super().save(*args, **kwargs)
        

class Subcategory_post(models.Model):
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(to=Subcategory_post, on_delete=models.CASCADE)
    

class Subcategory_survey(models.Model):
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(to=Subcategory_survey, on_delete=models.CASCADE)
    

class Subcategory_test(models.Model):
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(to=Subcategory_test, on_delete=models.CASCADE)
    
    
class Subcategory_quest(models.Model):
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(to=Subcategory_quest, on_delete=models.CASCADE)
    

class Subcategory_album(models.Model):
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(to=Subcategory_album, on_delete=models.CASCADE)


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
        

class Percent_for_content(models.Model):
    percent = models.IntegerField(verbose_name="percent_for_content", default=30)

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
    if Percent_for_content.objects.all().count() == 0:
        Percent_for_content.objects.create()


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
