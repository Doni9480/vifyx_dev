from django.db import models
from django.conf import settings
from blog.managers import LevelAccessManager
from blogs.models import Blog, LevelAccess
from django.template.defaultfilters import slugify as default_slugify
from transliterate import slugify
from django_cleanup import cleanup
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


class Album(models.Model):
    level_access_objects = LevelAccessManager()
    objects = models.Manager()

    slug = models.SlugField(
        verbose_name="URL", max_length=255, unique=True, db_index=True
    )
    preview = models.ImageField(
        verbose_name="Preview", upload_to=upload_to("uploads/albums/previews"), null=True, blank=True
    )
    size = models.IntegerField(blank=True, verbose_name='Size preview (KB)', null=True)
    title = models.CharField(
        verbose_name="Title", null=False, blank=False, max_length=255
    )
    description = models.TextField(verbose_name='Description')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )
    language = models.CharField(
        max_length=255,
        verbose_name="Language"
    )
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE, verbose_name='Category')
    subcategory = models.ForeignKey(to=Subcategory, on_delete=models.CASCADE, verbose_name='Subcategory', null=True, blank=True)
    hide_to_user = models.BooleanField(default=False, verbose_name="Hide to user")
    hide_to_moderator = models.BooleanField(
        default=False, verbose_name="Hide to moderator"
    )
    namespace = models.CharField(verbose_name='Namespace', default='albums')
    blog = models.ForeignKey(to=Blog, on_delete=models.CASCADE)
    level_access = models.ForeignKey(to=LevelAccess, on_delete=models.CASCADE, verbose_name='Level access', null=True, blank=True)

    date = models.DateTimeField(auto_now_add=True)
    preview_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Album"
        verbose_name_plural = "Albums"
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_preview = self.preview

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.blog.is_private and self.level_access:
            self.level_access = None
            
        if self.preview and self.preview.path != self.__original_preview.path:
            self.size = self.preview.size
            self.preview = change_size(self.preview)
            self.preview_date = timezone.now()
            
        if not self.slug:
            title = default_slugify(self.title)  # title on english language
            if not title:
                title = slugify(self.title)  # title on russian language
            strtime = "".join(str(time.time()).split("."))
            self.slug = "%s-%s" % (strtime[7:], title)
        super(Album, self).save(*args, **kwargs)
        

class AlbumLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='user_album_like')
    album = models.ForeignKey(to=Album, on_delete=models.CASCADE, verbose_name='Album', null=True, related_name='album_like')
        

class AlbumPhoto(models.Model):
    album = models.ForeignKey(to=Album, on_delete=models.CASCADE, verbose_name='Album')
    photo = models.ImageField(verbose_name="Preview", upload_to=upload_to("uploads/albums/photos"))
    size = models.IntegerField(blank=True, verbose_name='Size photo (KB)', null=True)
    photo_date = models.DateTimeField(auto_now_add=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_photo = self.photo
    
    def save(self, *args, **kwargs):
        if self.photo and self.photo.path != self.__original_photo.path:
            self.size = self.photo.size
            self.photo = change_size(self.photo.path)
            self.photo_date = timezone.now()
        super(AlbumPhoto, self).save(*args, **kwargs)
        

class AlbumWeekView(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='user_album_week')
    album = models.ForeignKey(to=Album, on_delete=models.CASCADE, verbose_name='Album', null=True, related_name='album_week')


class AlbumDayView(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='user_album_day')
    album = models.ForeignKey(to=Album, on_delete=models.CASCADE, verbose_name='Album', null=True, related_name='album_day')


class AlbumView(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True
    )
    album = models.ForeignKey(
        to=Album, on_delete=models.CASCADE, verbose_name="Album", null=True
    )

    class Meta:
        verbose_name = "View"
        verbose_name_plural = "Views"
        

class AlbumTag(models.Model):
    title = models.CharField(
        verbose_name="Title", max_length=255, blank=False, null=False
    )
    album = models.ForeignKey(to=Album, on_delete=models.CASCADE, verbose_name="Album")

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self):
        return self.title

        
@cleanup.ignore
class DraftAlbum(models.Model):
    preview = models.ImageField(
        verbose_name="Preview", upload_to=upload_to("uploads/albums/drafts/previews"), null=True, blank=True
    )
    title = models.CharField(
        verbose_name="Title", null=True, blank=True, max_length=255
    )
    description = models.TextField(verbose_name='Description', null=True, blank=True)
    blog = models.ForeignKey(to=Blog, on_delete=models.CASCADE)
    level_access = models.ForeignKey(to=LevelAccess, on_delete=models.CASCADE, verbose_name='Level access', null=True, blank=True)
    language = models.CharField(max_length=255, verbose_name='Language', null=True, blank=True)
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE, verbose_name='Category', null=True, blank=True)
    subcategory = models.ForeignKey(to=Subcategory, on_delete=models.CASCADE, verbose_name='Subcategory', null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )

    class Meta:
        verbose_name = "Draft"
        verbose_name_plural = "Drafts"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.preview:
            self.preview = change_size(self.preview)
        if not self.blog.is_private and self.level_access:
            self.level_access = 0
        super(DraftAlbum, self).save(*args, **kwargs)
        

class DraftAlbumTag(models.Model):
    title = models.CharField(
        verbose_name="Title", max_length=255, blank=False, null=False
    )
    draft = models.ForeignKey(
        to=DraftAlbum, on_delete=models.CASCADE, verbose_name="Draft"
    )

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self):
        return self.title

        
class DraftAlbumPhoto(models.Model):
    draft_album = models.ForeignKey(to=DraftAlbum, on_delete=models.CASCADE, verbose_name='Draft album')
    photo = models.ImageField(verbose_name="Preview", upload_to=upload_to("uploads/albums/drafts/photos"))
    
    def save(self, *args, **kwargs):
        if self.photo:
            self.photo = change_size(self.photo.path)
        super(DraftAlbumPhoto, self).save(*args, **kwargs)