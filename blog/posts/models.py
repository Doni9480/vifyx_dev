import os
import time

from django.db import models
from django.conf import settings
from django_cleanup import cleanup
from django.dispatch import receiver
from django.db.models.signals import post_delete
from django.template.defaultfilters import slugify as default_slugify
from transliterate import slugify

from blogs.models import Blog

from blog.managers import LevelAccessManager


class Post(models.Model):
    level_access_objects = LevelAccessManager()
    objects = models.Manager()

    languages = (
        ("1", "English"),
        ("2", "Russian"),
    )

    slug = models.SlugField(
        verbose_name="URL", max_length=255, unique=True, db_index=True
    )
    preview = models.ImageField(
        verbose_name="Preview", upload_to="uploads/", null=False, blank=False
    )
    title = models.CharField(
        verbose_name="Title", null=False, blank=False, max_length=255
    )
    description = models.TextField(verbose_name="Description", null=False, blank=False)
    content = models.TextField(verbose_name="Content", blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )
    language = models.CharField(
        verbose_name="Language", max_length=255, choices=languages
    )
    scores = models.IntegerField(verbose_name="scores", default=0)
    mouth_scores = models.IntegerField(verbose_name="Mouth scores", default=0)
    hide_to_user = models.BooleanField(default=False, verbose_name="Hide to user")
    hide_to_moderator = models.BooleanField(
        default=False, verbose_name="Hide to moderator"
    )
    blog = models.ForeignKey(to=Blog, on_delete=models.CASCADE)
    level_access = models.IntegerField(verbose_name="Level access", default=0)

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
    languages = (
        ("1", "English"),
        ("2", "Russian"),
    )

    preview = models.ImageField(
        verbose_name="Preview", upload_to="uploads_drafts/", null=True, blank=True
    )
    title = models.CharField(
        verbose_name="Title", null=True, blank=True, max_length=255
    )
    description = models.TextField(verbose_name="Description", null=True, blank=True)
    content = models.TextField(verbose_name="Content", blank=True, null=True)
    blog = models.ForeignKey(to=Blog, on_delete=models.CASCADE)
    level_access = models.IntegerField(verbose_name="Level access", default=0)
    user = models.OneToOneField(
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
