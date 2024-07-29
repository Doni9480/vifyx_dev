from django.db import models
from django.conf import settings

from blog.managers import TestShowManager

from django.template.defaultfilters import slugify as default_slugify
from transliterate import slugify
from blogs.models import Blog, LevelAccess

from custom_tests.managers import LevelAccessManager

import time


class Category(models.Model):
    category = models.CharField(verbose_name='Category')
    
    def __str__(self):
        return self.category
    
    
class Subcategory(models.Model):
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE, verbose_name='Category')
    subcategory = models.CharField(verbose_name='Subcategory')

    def __str__(self):
        return self.subcategory


class Test(models.Model):
    objects = models.Manager()
    objects_show = TestShowManager()
    level_access_objects = LevelAccessManager()
    
    slug = models.SlugField(
        verbose_name="URL",
        max_length=255,
        unique=True,
        db_index=True,
    )
    preview = models.ImageField(
        verbose_name="Preview",
        upload_to="uploads/",
        null=True,
        blank=True,
    )
    title = models.CharField(
        verbose_name="Title",
        null=False,
        blank=False,
        max_length=255,
    )
    description = models.TextField(
        verbose_name="Description",
        null=True,
        blank=True,
    )
    content = models.TextField(
        verbose_name="Content",
        blank=True,
        null=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    language = models.CharField(
        max_length=255,
        verbose_name="Language",
    )
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE, verbose_name='Category')
    subcategory = models.ForeignKey(to=Subcategory, on_delete=models.CASCADE, verbose_name='Subcategory')
    scores = models.IntegerField(
        verbose_name="scores",
        default=0,
    )
    namespace = models.CharField(verbose_name='Namespace', default='posts')
    hide_to_moderator = models.BooleanField(
        default=False,
        verbose_name="Hide to moderator",
    )
    hide_to_user = models.BooleanField(
        default=False,
        verbose_name="Hide to user",
    )
    hidden = models.BooleanField(
        default=False,
        verbose_name='Hidden for post',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    timer = models.IntegerField(
        null=True,
        blank=True,
        help_text="Example: 10 (minute) or leave blank",
        verbose_name="Timer",
    )
    blog = models.ForeignKey(
        to=Blog, 
        on_delete=models.CASCADE
    )
    level_access = models.ForeignKey(
        to=LevelAccess, 
        on_delete=models.CASCADE, 
        verbose_name='Level access', 
        null=True, 
        blank=True
    )
    date = models.DateTimeField(
        auto_now_add=True
    )

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

        super(Test, self).save()
        

class TestView(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True
    )
    test = models.ForeignKey(
        to=Test, on_delete=models.CASCADE, verbose_name="Test", null=True
    )

    class Meta:
        verbose_name = "View"
        verbose_name_plural = "Views"


class Question(models.Model):
    question = models.TextField(
        verbose_name="Question",
    )
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name="Тест",
    )

    def __str__(self):
        return f"{self.question} - {self.test}"


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
