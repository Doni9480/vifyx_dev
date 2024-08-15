from django.db import models
from django.conf import settings
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError


class Blog(models.Model):
    slug = models.CharField(
        verbose_name="URL", null=False, blank=False, validators=[MinLengthValidator(5)], max_length=40, unique=True
    )
    preview = models.ImageField(verbose_name="Preview", upload_to="upload_blogs/")
    title = models.CharField(
        verbose_name="Title", null=False, blank=False, max_length=255
    )
    description = models.TextField(
        verbose_name="Description", null=False, blank=False
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True
    )
    is_private = models.BooleanField(verbose_name="Is private", default=False)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Blog"
        verbose_name_plural = "Blogs"

    def __str__(self):
        return self.title
    

class Donate(models.Model):
    message = models.CharField(verbose_name='Message', max_length=200)
    amount = models.IntegerField(verbose_name='Amount')
    blog = models.ForeignKey(to=Blog, on_delete=models.CASCADE, verbose_name="Blog")
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="User", null=True)
    date = models.DateTimeField(auto_now_add=True)


class LevelAccess(models.Model):
    preview = models.ImageField(verbose_name="Preview", upload_to="upload_follows/")
    title = models.CharField(max_length=255, verbose_name="Title", unique=True)
    description = models.TextField(verbose_name="Description")
    level = models.IntegerField(verbose_name="Level access")
    scores = models.IntegerField(verbose_name="Scores", default=0)
    blog = models.ForeignKey(to=Blog, on_delete=models.CASCADE, verbose_name="Blog")


class PaidFollow(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateTimeField(verbose_name="Expiration date", null=True)
    count_months = models.IntegerField(verbose_name="Count months", default=1)
    blog_access_level = models.ForeignKey(
        to=LevelAccess, on_delete=models.CASCADE, verbose_name="blog level access"
    )
    blog = models.ForeignKey(to=Blog, on_delete=models.CASCADE, verbose_name="Blog")


class BlogFollow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="follower"
    )
    blog = models.ForeignKey(to=Blog, on_delete=models.CASCADE, verbose_name="Blog")    
