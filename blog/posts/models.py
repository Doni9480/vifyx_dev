import os
import time

from django.db import models
from django.conf import settings
from django_cleanup import cleanup
from django.dispatch import receiver
from django.db.models.signals import post_delete
from django.template.defaultfilters import slugify as default_slugify
from transliterate import slugify
from django.core.exceptions import ValidationError

from blogs.models import Blog, LevelAccess

from custom_tests.models import Test


class LevelAccessManager(models.Manager):
    def get_queryset(self):
        return super(LevelAccessManager, self).get_queryset().filter(level_access=None, is_paid=False)


class Category(models.Model):
    category_rus = models.CharField(verbose_name='Category rus')
    category_eng = models.CharField(verbose_name='Category eng')
    
    def __str__(self):
        return self.category_eng
    
    
class Subcategory(models.Model):
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE, verbose_name='Category')
    subcategory_rus = models.CharField(verbose_name='Subcategory rus')
    subcategory_eng = models.CharField(verbose_name='Subcategory eng')

    def __str__(self):
        return self.subcategory_eng
    

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
        max_length=255,
        verbose_name="Language"
    )
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE, verbose_name='Category')
    subcategory = models.ForeignKey(to=Subcategory, on_delete=models.CASCADE, verbose_name='Subcategory', null=True, blank=True)
    scores = models.IntegerField(verbose_name="scores", default=0)
    mouth_scores = models.IntegerField(verbose_name="Mouth scores", default=0)
    hide_to_user = models.BooleanField(default=False, verbose_name="Hide to user")
    hide_to_moderator = models.BooleanField(
        default=False, verbose_name="Hide to moderator"
    )
    test = models.OneToOneField(to=Test, verbose_name='Test', on_delete=models.CASCADE, null=True, blank=True)
    namespace = models.CharField(verbose_name='Namespace', default='posts')
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
            self.level_access = None

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


class PostWeekView(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='user_post_week')
    post = models.ForeignKey(to=Post, on_delete=models.CASCADE, verbose_name='Post', null=True, related_name='post_week')


class PostDayView(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='user_post_day')
    post = models.ForeignKey(to=Post, on_delete=models.CASCADE, verbose_name='Post', null=True, related_name='post_day')


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
    instance = kwargs['instance']
    images = []
    html_str = instance.content

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
    
    if instance.test:
        instance.test.delete() # delete test


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
    language = models.CharField(max_length=255, verbose_name='Language', null=True, blank=True)
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE, verbose_name='Category', null=True, blank=True)
    subcategory = models.ForeignKey(to=Subcategory, on_delete=models.CASCADE, verbose_name='Subcategory', null=True, blank=True)
    add_survey = models.BooleanField(verbose_name="Add survey", default=False)
    is_paid = models.BooleanField(verbose_name="Is paid", default=False)
    is_create_test = models.BooleanField(verbose_name='Test', default=False)
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


def validate_only_one_instance(obj):
    model = obj.__class__
    if model.objects.count() > 0 and obj.id != model.objects.get().id:
        raise ValidationError("Can only create 1 %s instance" % model.__name__)
    
class Banner(models.Model):
    text = models.CharField(verbose_name='Pit it to the main page')
    post_slug = models.CharField(verbose_name='Post slug')

    def clean(self):
        validate_only_one_instance(self)