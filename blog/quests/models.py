from django.db import models
from django.conf import settings
from mptt.models import MPTTModel, TreeForeignKey


class Quest(models.Model):
    slug = models.SlugField(
        verbose_name="URL",
        max_length=255,
        unique=True,
        db_index=True,
    )
    preview = models.ImageField(
        verbose_name="Preview",
        upload_to="quests/",
        null=True,
        blank=True,
    )
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

    def __str__(self):
        return self.title


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