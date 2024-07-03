from django.db import models

from posts.models import Post

from surveys.models import Survey

from users.models import User


class NotificationPost(models.Model):
    post = models.ForeignKey(to=Post, on_delete=models.CASCADE, verbose_name='Post')
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name='user', null=True)
    is_read = models.BooleanField(verbose_name='Is read', default=False)


class NotificationSurvey(models.Model):
    survey = models.ForeignKey(to=Survey, on_delete=models.CASCADE, verbose_name='Survey')
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name='user', null=True)
    is_read = models.BooleanField(verbose_name='Is read', default=False)