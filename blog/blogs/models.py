from django.db import models
from django.conf import settings
from django.template.defaultfilters import slugify as default_slugify

from transliterate import slugify

import time


class Blog(models.Model):
    slug = models.SlugField(
        verbose_name="URL", max_length=255, unique=True, db_index=True
    )
    preview = models.ImageField(verbose_name="Preview", upload_to="upload_blogs/")
    title = models.CharField(
        verbose_name="Title", null=False, blank=False, max_length=255
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

    def save(self, *args, **kwargs):
        if not self.slug:
            title = default_slugify(self.title)  # title on english language
            if not title:
                title = slugify(self.title)  # title on russian language

            strtime = "".join(str(time.time()).split("."))
            self.slug = "%s-%s" % (strtime[7:], title)

        super(Blog, self).save()


class LevelAccess(models.Model):
    level = models.IntegerField(verbose_name="Level access")
    scores = models.IntegerField(verbose_name="Scores", default=0)
    blog = models.ForeignKey(to=Blog, on_delete=models.CASCADE, verbose_name="Blog")


class PaidFollow(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateTimeField(verbose_name="Expiration date", null=True)
    count_mouths = models.IntegerField(verbose_name="Count mouths", default=1)
    blog_access_level = models.ForeignKey(
        to=LevelAccess, on_delete=models.CASCADE, verbose_name="blog level access"
    )
    blog = models.ForeignKey(to=Blog, on_delete=models.CASCADE, verbose_name="Blog")
