from django.db import models

from users.models import User

from posts.models import Post

from surveys.models import Survey

from custom_tests.models import Test

from quests.models import Quest


class Comment(models.Model):
    user = models.ForeignKey(
        to=User, on_delete=models.CASCADE, verbose_name="User", null=True
    )
    post = models.ForeignKey(
        to=Post, on_delete=models.CASCADE, verbose_name="Post", null=True
    )
    survey = models.ForeignKey(
        to=Survey, on_delete=models.CASCADE, verbose_name="Survey", null=True
    )
    test = models.ForeignKey(
        to=Test, on_delete=models.CASCADE, verbose_name="Test", null=True, blank=True
    )
    quest = models.ForeignKey(
        to=Quest, on_delete=models.CASCADE, verbose_name="Quest", null=True, blank=True
    )
    text = models.TextField(verbose_name="Text_comment")
    delete_from_user = models.BooleanField(
        default=False, verbose_name="Delete_from_user"
    )
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return self.text


class Answer(models.Model):
    user = models.ForeignKey(
        to=User, on_delete=models.CASCADE, verbose_name="User", null=True
    )
    post = models.ForeignKey(
        to=Post, on_delete=models.CASCADE, verbose_name="Post", null=True
    )
    survey = models.ForeignKey(
        to=Survey, on_delete=models.CASCADE, verbose_name="Survey", null=True
    )
    comment = models.ForeignKey(
        to=Comment, on_delete=models.CASCADE, verbose_name="Comment"
    )
    test = models.ForeignKey(
        to=Test, on_delete=models.CASCADE, verbose_name="Test", null=True, blank=True
    )
    quest = models.ForeignKey(
        to=Quest, on_delete=models.CASCADE, verbose_name="Quest", null=True, blank=True
    )
    text = models.TextField(verbose_name="Text_answer")
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Answer"
        verbose_name_plural = "Answers"

    def __str__(self):
        return self.text
