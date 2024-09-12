from typing import Iterable
from django.db import models
from django.template.defaultfilters import slugify as default_slugify
from django.conf import settings
from transliterate import slugify
from django import utils
from blog.validators import check_language
from contests.api.validators import check_item_type, check_criteries
from posts.models import Post
from quests.models import Quest
from albums.models import Album
from blog.utils import upload_to, change_size
from django.utils import timezone
import time


class Contest(models.Model):
    LANGUAGE_CHOICES = (
        ('english', 'English'),
        ('russian', 'Russian'),
    )
    ITEM_TYPE_CHOICES = (
        ('post', 'Post'),
        ('album', 'Album'),
        ('quest', 'Quest')
    )
    CRITERIES_CHOICES = (
        ('likes', 'Likes'),
        ('views', 'Views'),
        ('assessment', 'Assessment')
    )
    
    preview = models.ImageField(
        verbose_name="Preview", upload_to=upload_to("uploads/contests/previews"), null=True, blank=True
    )
    size = models.IntegerField(verbose_name='Size preview (KB)', null=True, blank=True)
    title = models.CharField(
        verbose_name="Title", null=False, blank=False, max_length=255
    )
    description = models.TextField(verbose_name='Description', null=True, blank=True)
    start_date = models.DateTimeField(verbose_name='Start date', default=utils.timezone.now)
    end_date = models.DateTimeField(verbose_name='End date')
    slug = models.SlugField(
        verbose_name="URL", max_length=255, unique=True, db_index=True, null=True, blank=True
    ) 
    item_type = models.CharField(
        verbose_name='Item type', 
        validators=[check_item_type],
        choices=ITEM_TYPE_CHOICES,
    )
    language = models.CharField(
        max_length=255,
        verbose_name="Language",
        validators=[check_language],
        choices=LANGUAGE_CHOICES,
    )
    criteries = models.CharField(
        verbose_name='Criteries', 
        validators=[check_criteries],
        choices=CRITERIES_CHOICES
    )
    is_end = models.BooleanField(verbose_name='Is end', default=False)
    preview_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Contest"
        verbose_name_plural = "Contests"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_preview = self.preview

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.preview and self.preview.path != self.__original_preview.path:
            self.size = self.preview.size
            self.preview = change_size(self.preview.path)
            self.preview_date = timezone.now()
        if not self.slug:
            title = default_slugify(self.title)  # title on english language
            if not title:
                title = slugify(self.title)  # title on russian language

            strtime = "".join(str(time.time()).split("."))
            self.slug = "%s-%s" % (strtime[7:], title)
        super(Contest, self).save(*args, **kwargs)
        

class PostElement(models.Model):
    post = models.ForeignKey(to=Post, on_delete=models.CASCADE)
    contest = models.ForeignKey(to=Contest, on_delete=models.CASCADE)
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    
class QuestElement(models.Model):
    quest = models.ForeignKey(to=Quest, on_delete=models.CASCADE)
    contest = models.ForeignKey(to=Contest, on_delete=models.CASCADE)
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    

class AlbumElement(models.Model):
    album = models.ForeignKey(to=Album, on_delete=models.CASCADE)
    contest = models.ForeignKey(to=Contest, on_delete=models.CASCADE)
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    

class PrizePostElement(models.Model):
    contest = models.ForeignKey(to=Contest, on_delete=models.CASCADE, related_name='contest_post_place')
    one_place = models.ForeignKey(to=Post, blank=True, null=True, on_delete=models.CASCADE, related_name='one_post_place')
    two_place = models.ForeignKey(to=Post, blank=True, null=True, on_delete=models.CASCADE, related_name='two_post_place')
    three_place = models.ForeignKey(to=Post, blank=True, null=True, on_delete=models.CASCADE, related_name='three_post_place')
    four_lace = models.ForeignKey(to=Post, blank=True, null=True, on_delete=models.CASCADE, related_name='four_post_place')
    five_place = models.ForeignKey(to=Post, blank=True, null=True, on_delete=models.CASCADE, related_name='five_post_place')
    six_place = models.ForeignKey(to=Post, blank=True, null=True, on_delete=models.CASCADE, related_name='six_post_place')
    seven_place = models.ForeignKey(to=Post, blank=True, null=True, on_delete=models.CASCADE, related_name='seven_post_place')
    eight_place = models.ForeignKey(to=Post, blank=True, null=True, on_delete=models.CASCADE, related_name='eight_post_place')
    nine_place = models.ForeignKey(to=Post, blank=True, null=True, on_delete=models.CASCADE, related_name='nine_post_place')
    ten_place = models.ForeignKey(to=Post, blank=True, null=True, on_delete=models.CASCADE, related_name='ten_post_place')
    
    class Meta:
        verbose_name = "Post prize"
        verbose_name_plural = "Post prizes"
    
    def save(self, *args, **kwargs):
        if not self.contest.is_end:
            self.contest.is_end = True
            self.contest.save()
        super(PrizePostElement, self).save()
    

class PrizeAlbumElement(models.Model):
    contest = models.ForeignKey(to=Contest, on_delete=models.CASCADE, related_name='contest_album_place')
    one_place = models.ForeignKey(to=Album, null=True, blank=True, on_delete=models.CASCADE, related_name='one_album_place')
    two_place = models.ForeignKey(to=Album, null=True, blank=True, on_delete=models.CASCADE, related_name='two_album_place')
    three_place = models.ForeignKey(to=Album, null=True, blank=True, on_delete=models.CASCADE, related_name='three_album_place')
    four_lace = models.ForeignKey(to=Album, null=True, blank=True, on_delete=models.CASCADE, related_name='four_album_place')
    five_place = models.ForeignKey(to=Album, null=True, blank=True, on_delete=models.CASCADE, related_name='five_album_place')
    six_place = models.ForeignKey(to=Album, null=True, blank=True, on_delete=models.CASCADE, related_name='six_album_place')
    seven_place = models.ForeignKey(to=Album, null=True, blank=True, on_delete=models.CASCADE, related_name='seven_album_place')
    eight_place = models.ForeignKey(to=Album, null=True, blank=True, on_delete=models.CASCADE, related_name='eight_album_place')
    nine_place = models.ForeignKey(to=Album, null=True, blank=True, on_delete=models.CASCADE, related_name='nine_album_place')
    ten_place = models.ForeignKey(to=Album, null=True, blank=True, on_delete=models.CASCADE, related_name='ten_album_place')
    
    class Meta:
        verbose_name = "Album prize"
        verbose_name_plural = "Album prizes"

    def save(self, *args, **kwargs):
        if not self.contest.is_end:
            self.contest.is_end = True
            self.contest.save()
        super(PrizeAlbumElement, self).save()
    

class PrizeQuestElement(models.Model):
    contest = models.ForeignKey(to=Contest, on_delete=models.CASCADE, related_name='contest_quest_place')
    one_place = models.ForeignKey(to=Quest, null=True, blank=True, on_delete=models.CASCADE, related_name='one_quest_place')
    two_place = models.ForeignKey(to=Quest, null=True, blank=True, on_delete=models.CASCADE, related_name='two_quest_place')
    three_place = models.ForeignKey(to=Quest, null=True, blank=True, on_delete=models.CASCADE, related_name='three_quest_place')
    four_lace = models.ForeignKey(to=Quest, null=True, blank=True, on_delete=models.CASCADE, related_name='four_quest_place')
    five_place = models.ForeignKey(to=Quest, null=True, blank=True, on_delete=models.CASCADE, related_name='five_quest_place')
    six_place = models.ForeignKey(to=Quest, null=True, blank=True, on_delete=models.CASCADE, related_name='six_quest_place')
    seven_place = models.ForeignKey(to=Quest, null=True, blank=True, on_delete=models.CASCADE, related_name='seven_quest_place')
    eight_place = models.ForeignKey(to=Quest, null=True, blank=True, on_delete=models.CASCADE, related_name='eight_quest_place')
    nine_place = models.ForeignKey(to=Quest, null=True, blank=True, on_delete=models.CASCADE, related_name='nine_quest_place')
    ten_place = models.ForeignKey(to=Quest, null=True, blank=True, on_delete=models.CASCADE, related_name='ten_quest_place')

    class Meta:
        verbose_name = "Quest prize"
        verbose_name_plural = "Quest prizes"
    
    def save(self, *args, **kwargs):
        if not self.contest.is_end:
            self.contest.is_end = True
            self.contest.save()
        super(PrizeQuestElement, self).save()
