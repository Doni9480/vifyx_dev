from django.db import models
from django.conf import settings


class Test(models.Model):
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
    scores = models.IntegerField(
        verbose_name="scores",
        default=0,
    )
    hide_to_moderator = models.BooleanField(
        default=False,
        verbose_name="Hide to moderator",
    )
    hide_to_user = models.BooleanField(
        default=True,
        verbose_name="Hide to user",
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

    def __str__(self):
        return self.title


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
