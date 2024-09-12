from django.db import models
from django.conf import settings
from mptt.models import MPTTModel, TreeForeignKey
from blogs.models import Blog, LevelAccess
from blog.managers import LevelAccessManager
from django.template.defaultfilters import slugify as default_slugify
from transliterate import slugify
from blog.utils import upload_to, change_size
from django.utils import timezone
import time


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


class Quest(models.Model):
    objects = models.Manager()
    level_access_objects = LevelAccessManager()
    
    slug = models.SlugField(
        verbose_name="URL",
        max_length=255,
        unique=True,
        db_index=True,
    )
    preview = models.ImageField(
        verbose_name="Preview",
        upload_to=upload_to("uploads/quests/previews"),
        null=True,
        blank=True,
    )
    size = models.IntegerField(verbose_name='Size preview (KB)', null=True, blank=True)
    title = models.CharField(
        verbose_name="Title",
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
        verbose_name="Scores",
        default=0,
    )
    namespace = models.CharField(verbose_name='Namespace', default='quests')
    hide_to_user = models.BooleanField(
        default=False,
        verbose_name="Hide to User",
    )
    hide_to_moderator = models.BooleanField(
        default=False,
        verbose_name="Hide to Moderator",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    timer = models.PositiveIntegerField(
        null=True,
        blank=True,
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
    preview_date = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_preview = self.preview
    
    def save(self, *args, **kwargs):
        if self.preview and self.preview.path != self.__original_preview.path:
            self.size = self.preview.size        
            self.preview = change_size(self.preview.path)
            self.preview_date = timezone.now()
        if not self.blog.is_private and self.level_access:
            self.level_access = None

        if not self.slug:
            title = default_slugify(self.title)  # title on english language
            if not title:
                title = slugify(self.title)  # title on russian language

            strtime = "".join(str(time.time()).split("."))
            self.slug = "%s-%s" % (strtime[7:], title)

        super(Quest, self).save(*args, **kwargs)
        

class QuestTag(models.Model):
    title = models.CharField(
        verbose_name="Title", max_length=255, blank=False, null=False
    )
    quest = models.ForeignKey(to=Quest, on_delete=models.CASCADE, verbose_name="Quest")

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self):
        return self.title
        
        
class QuestLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='user_quest_like')
    quest = models.ForeignKey(to=Quest, on_delete=models.CASCADE, verbose_name='Quest', null=True, related_name='quest_like')
        
        
class QuestWeekView(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='user_quest_week')
    quest = models.ForeignKey(to=Quest, on_delete=models.CASCADE, verbose_name='Quest', null=True, related_name='quest_week')


class QuestDayView(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='user_quest_day')
    quest = models.ForeignKey(to=Quest, on_delete=models.CASCADE, verbose_name='Quest', null=True, related_name='quest_day')
    
    
class QuestView(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True
    )
    quest = models.ForeignKey(
        to=Quest, on_delete=models.CASCADE, verbose_name="quest", null=True
    )

    class Meta:
        verbose_name = "View"
        verbose_name_plural = "Views"


class QuestionQuest(MPTTModel):
    text = models.CharField(max_length=255)
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )
    quest = models.ForeignKey(
        Quest,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="Quest",
    )

    class MPTTMeta:
        order_insertion_by = ["text"]

    def __str__(self):
        return self.text


class Result(models.Model):
    content = models.TextField(
        verbose_name="Content",
    )

    def __str__(self):
        return self.content


class QuestionQuestAnswer(models.Model):
    text = models.CharField(max_length=255)
    question = models.ForeignKey(
        QuestionQuest,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    next_question = models.ForeignKey(
        QuestionQuest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="previous_answers",
    )
    result = models.ForeignKey(
        Result,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="answer",
    )

    def __str__(self):
        return self.text