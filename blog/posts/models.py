import os
import time

from django.db import models
from django.conf import settings
from django_cleanup import cleanup
from django.dispatch import receiver
from django.db.models.signals import post_delete
from django.template.defaultfilters import slugify as default_slugify
from transliterate import slugify

from blogs.models import Blog, LevelAccess

from blog.managers import LevelAccessManager


class Post(models.Model):
    level_access_objects = LevelAccessManager()
    objects = models.Manager()

    slug = models.SlugField(
        verbose_name="URL", max_length=255, unique=True, db_index=True
    )
    preview = models.ImageField(
        verbose_name="Preview", upload_to="uploads/", null=True, blank=True
    )
    title = models.CharField(
        verbose_name="Title", null=False, blank=False, max_length=255
    )
    content = models.TextField(verbose_name="Content")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )
    language = models.CharField(
        verbose_name="Language"
    )
    scores = models.IntegerField(verbose_name="scores", default=0)
    mouth_scores = models.IntegerField(verbose_name="Mouth scores", default=0)
    hide_to_user = models.BooleanField(default=False, verbose_name="Hide to user")
    hide_to_moderator = models.BooleanField(
        default=False, verbose_name="Hide to moderator"
    )
    add_survey = models.BooleanField(verbose_name="Add survey", default=False)
    is_paid = models.BooleanField(verbose_name="Is paid", default=False)
    amount = models.IntegerField(verbose_name="Amount", blank=True, null=True)
    blog = models.ForeignKey(to=Blog, on_delete=models.CASCADE)
    level_access = models.ForeignKey(to=LevelAccess, on_delete=models.CASCADE, verbose_name='Level access', null=True, blank=True)

    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.blog.is_private and self.level_access:
            self.level_access = 0

        if not self.slug:
            title = default_slugify(self.title)  # title on english language
            if not title:
                title = slugify(self.title)  # title on russian language

            strtime = "".join(str(time.time()).split("."))
            self.slug = "%s-%s" % (strtime[7:], title)

        super(Post, self).save()
        

class PostRadio(models.Model):
    post = models.ForeignKey(to=Post, on_delete=models.CASCADE, verbose_name='Post')
    scores = models.IntegerField(verbose_name='scores', default=0)
    title = models.CharField(max_length=255, verbose_name="title")
    
    class Meta:
        verbose_name = 'Radio'
        verbose_name_plural = 'Radios'
        
    def __str__(self):
        return self.title


class PostVote(models.Model):
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='User')
    post = models.ForeignKey(to=Post, on_delete=models.CASCADE, verbose_name='Post')
    option = models.ForeignKey(to=PostRadio, on_delete=models.CASCADE, verbose_name='Option', null=True)


class PostTag(models.Model):
    title = models.CharField(
        verbose_name="Title", max_length=255, blank=False, null=False
    )
    post = models.ForeignKey(to=Post, on_delete=models.CASCADE, verbose_name="Post")

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self):
        return self.title


class PostView(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True
    )
    post = models.ForeignKey(
        to=Post, on_delete=models.CASCADE, verbose_name="Post", null=True
    )

    class Meta:
        verbose_name = "View"
        verbose_name_plural = "Views"
        

class Question(models.Model):
    question = models.TextField(
        verbose_name="Question",
    )
    post = models.ForeignKey(
        to=Post,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name="Тест",
    )

    def __str__(self):
        return f"{self.question} - {self.post}"


class QuestionAnswer(models.Model):
    variant = models.CharField(
        max_length=250,
        verbose_name="Question answer",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="Question",
    )
    is_true = models.BooleanField(
        verbose_name="True Answer",
        default=False,
    )

    def __str__(self):
        return f"{self.variant} - {self.question}: {self.is_true}"
        

class BuyPost(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    post = models.ForeignKey(
        to=Post, on_delete=models.CASCADE, verbose_name="Post"
    )
    scores = models.IntegerField(verbose_name="scores")


@receiver(post_delete, sender=Post)
def on_delete(sender, **kwargs):
    images = []
    html_str = kwargs["instance"].content

    while "img" in html_str:
        left_enter = html_str.find("<img")
        html_str = html_str[left_enter:]
        right_enter = html_str.find(">") + 1
        images.append(html_str[:right_enter])
        html_str = html_str[right_enter:]

    for image in images:
        left_enter = image.find(settings.MEDIA_URL)
        image = image[left_enter + len(settings.MEDIA_URL) :]
        right_enter = image.find('"')
        path = os.path.join(settings.MEDIA_ROOT / image[:right_enter])
        os.remove(os.path.join(path))


@cleanup.ignore
class DraftPost(models.Model):
    preview = models.ImageField(
        verbose_name="Preview", upload_to="uploads_drafts/", null=True, blank=True
    )
    title = models.CharField(
        verbose_name="Title", null=True, blank=True, max_length=255
    )
    content = models.TextField(verbose_name="Content", blank=True, null=True)
    blog = models.ForeignKey(to=Blog, on_delete=models.CASCADE)
    level_access = models.ForeignKey(to=LevelAccess, on_delete=models.CASCADE, verbose_name='Level access', null=True, blank=True)
    language = models.CharField(verbose_name='Language', null=True, blank=True)
    add_survey = models.BooleanField(verbose_name="Add survey", default=False)
    is_paid = models.BooleanField(verbose_name="Is paid", default=False)
    amount = models.IntegerField(verbose_name="Amount", blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )

    class Meta:
        verbose_name = "Draft"
        verbose_name_plural = "Drafts"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.blog.is_private and self.level_access:
            self.level_access = 0

        super(DraftPost, self).save()


class DraftPostTag(models.Model):
    title = models.CharField(
        verbose_name="Title", max_length=255, blank=False, null=False
    )
    draft = models.ForeignKey(
        to=DraftPost, on_delete=models.CASCADE, verbose_name="Draft"
    )

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self):
        return self.title
    

class DraftPostRadio(models.Model):
    draft_post = models.ForeignKey(
        to=DraftPost, on_delete=models.CASCADE, verbose_name="Draft post"
    )
    title = models.CharField(max_length=255, verbose_name="title")

    class Meta:
        verbose_name = "Radio"
        verbose_name_plural = "Radios"

    def __str__(self):
        return self.title
    