from django.db import models
from django.conf import settings

from posts.models import Post
from surveys.models import Survey
from custom_tests.models import Test
from quests.models import Quest
from albums.models import Album
from blogs.models import Donate, Blog
from contests.models import Contest
from comments.models import Answer
    

class Ban(models.Model):
    text = models.CharField(default='You have been banned.', verbose_name='Text')
    

class Unban(models.Model):
    text = models.CharField(default='You have been unbanned.', verbose_name='Text')
    
    
class ExpiringFollow(models.Model):
    text = models.CharField(default='Your follow expires in 3 days.', verbose_name='Text')
    
    
class SystemText(models.Model):
    english = models.BooleanField(verbose_name='English', default=True)
    russian = models.BooleanField(verbose_name='Russian', default=True)
    title_rus = models.CharField(null=True, blank=True, verbose_name='Title rus')
    title_eng = models.CharField(null=True, blank=True, verbose_name='Title eng')
    text_rus = models.TextField(null=True, blank=True, verbose_name='Text rus')
    text_eng = models.TextField(null=True, blank=True, verbose_name='Text eng')
    
    def __str__(self):
        return self.title_eng
    

class AnswerNotification(models.Model):
    answer = models.ForeignKey(to=Answer, on_delete=models.CASCADE, verbose_name='Answer')
    namespace = models.CharField(verbose_name='Namespace')
    slug = models.CharField(verbose_name='Slug')
    

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
    
    system_text = models.ForeignKey(to=SystemText, on_delete=models.CASCADE, null=True)
    
    ban = models.ForeignKey(to=Ban, on_delete=models.CASCADE, verbose_name='Ban', null=True)
    unban = models.ForeignKey(to=Unban, on_delete=models.CASCADE, verbose_name='Unban', null=True)
    
    expiring_follow = models.ForeignKey(to=ExpiringFollow, on_delete=models.CASCADE, verbose_name='Expiring follow', null=True)
    
    answer_notification = models.ForeignKey(to=AnswerNotification, on_delete=models.CASCADE, verbose_name='Answer notification', null=True)
    
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='User')
    is_read = models.BooleanField(verbose_name='Is read', default=False)
    date = models.DateTimeField(auto_now_add=True)
    
    
class NotificationBlog(models.Model):
    blog = models.ForeignKey(to=Blog, on_delete=models.CASCADE, verbose_name='Blog')
    follower = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Follower')
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='User of blog', related_name="user_of_blog")
    get_notifications_blog = models.BooleanField(default=True, verbose_name="Get notifications for blog")
    get_notifications_quest = models.BooleanField(default=True, verbose_name="Get notifications for quest")
    get_notifications_post = models.BooleanField(default=True, verbose_name="Get notifications for post")
    get_notifications_album = models.BooleanField(default=True, verbose_name="Get notifications for album")
    get_notifications_answer = models.BooleanField(default=True, verbose_name="Get notifications for answer")