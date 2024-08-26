from django.db import models
from django.conf import settings

from posts.models import Post
from surveys.models import Survey
from custom_tests.models import Test
from quests.models import Quest
from albums.models import Album
from users.models import User
from blogs.models import Donate, Blog
from contests.models import Contest
    

class Notification(models.Model):
    post = models.ForeignKey(to=Post, on_delete=models.CASCADE, verbose_name='Post', null=True)
    donate = models.ForeignKey(to=Donate, on_delete=models.CASCADE, verbose_name='Donate', null=True)
    survey = models.ForeignKey(to=Survey, on_delete=models.CASCADE, verbose_name='Survey', null=True)
    test = models.ForeignKey(to=Test, on_delete=models.CASCADE, verbose_name='Test', null=True)
    quest = models.ForeignKey(to=Quest, on_delete=models.CASCADE, verbose_name='Quest', null=True)
    album = models.ForeignKey(to=Album, on_delete=models.CASCADE, verbose_name='Album', null=True)
    contest_post = models.ForeignKey(to=Post, on_delete=models.CASCADE, verbose_name='Contest post', null=True, related_name='contest_post')
    contest_quest = models.ForeignKey(to=Quest, on_delete=models.CASCADE, verbose_name='Contest uest', null=True, related_name='contest_quest')
    contest_album = models.ForeignKey(to=Album, on_delete=models.CASCADE, verbose_name='Contest album', null=True, related_name='contest_album')
    contest = models.ForeignKey(to=Contest, on_delete=models.CASCADE, null=True)
    text = models.CharField(verbose_name='Text', null=True)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name='User')
    is_read = models.BooleanField(verbose_name='Is read', default=False)
    date = models.DateTimeField(auto_now_add=True)
    
    
class NotificationBlog(models.Model):
    blog = models.ForeignKey(to=Blog, on_delete=models.CASCADE, verbose_name='Blog')
    follower = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Follower')
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='User of blog', related_name="user_of_blog")
    get_notifications_blog = models.BooleanField(default=True, verbose_name="Get notifications for blog")