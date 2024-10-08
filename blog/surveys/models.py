import time
from blog.utils import upload_to, change_size
from django.db import models
from django.conf import settings
from django_cleanup import cleanup
from django.template.defaultfilters import slugify as default_slugify
from transliterate import slugify
from blogs.models import Blog, LevelAccess
from blog.managers import LevelAccessManager
from django.utils import timezone


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


class Survey(models.Model):
    objects = models.Manager()
    level_access_objects = LevelAccessManager()
    
    slug = models.SlugField(verbose_name='URL', max_length=255, unique=True, db_index=True)
    preview = models.ImageField(verbose_name='Preview', upload_to=upload_to('uploads/surveys/previews'), null=True, blank=True)
    size = models.IntegerField(blank=True, verbose_name='Size preview (KB)', null=True)
    title = models.CharField(verbose_name='Title', null=False, blank=False, max_length=255)
    description = models.TextField(verbose_name='Description', null=True, blank=True)
    content = models.TextField(verbose_name='Content', blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    language = models.CharField(max_length=255, verbose_name='Language')
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE, verbose_name='Category')
    subcategory = models.ForeignKey(to=Subcategory, on_delete=models.CASCADE, verbose_name='Subcategory', null=True, blank=True)
    namespace = models.CharField(verbose_name='Namespace', default='surveys')
    hide_to_user = models.BooleanField(default=False, verbose_name='Hide to user')
    hide_to_moderator = models.BooleanField(default=False, verbose_name='Hide to moderator')
    blog = models.ForeignKey(to=Blog, on_delete=models.CASCADE)
    level_access = models.ForeignKey(to=LevelAccess, on_delete=models.CASCADE, verbose_name='Level access', null=True, blank=True)
    
    date = models.DateTimeField(auto_now_add=True)
    preview_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Survey'
        verbose_name_plural = 'Surveys'
        
    def __str__(self):
        return self.title
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_preview = self.preview
    
    def save(self, *args, **kwargs):
        if self.preview:
            if self.pk is None or self.preview.path != self.__original_preview.path:
                self.size = self.preview.size
                self.preview = change_size(self.preview)
                self.preview_date = timezone.now()
                
        if not self.blog.is_private and self.level_access:
            self.level_access = None
            
        if not self.slug:
            title = default_slugify(self.title) # title on english language
            if not title:
                title = slugify(self.title) # title on russian language
                
            strtime = "".join(str(time.time()).split("."))
            self.slug = "%s-%s" % (strtime[7:], title)
        super(Survey, self).save(*args, **kwargs)
        

class SurveyTag(models.Model):
    title = models.CharField(verbose_name='Title', max_length=255, blank=False, null=False)
    survey = models.ForeignKey(to=Survey, on_delete=models.CASCADE, verbose_name='Survey')
    
    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        
    def __str__(self):
        return self.title
    

class SurveyLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='user_survey_like')
    survey = models.ForeignKey(to=Survey, on_delete=models.CASCADE, verbose_name='Survey', null=True, related_name='survey_like')
    

class SurveyWeekView(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='user_survey_week')
    survey = models.ForeignKey(to=Survey, on_delete=models.CASCADE, verbose_name='Survey', null=True, related_name='survey_week')


class SurveyDayView(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='user_survey_day')
    survey = models.ForeignKey(to=Survey, on_delete=models.CASCADE, verbose_name='Survey', null=True, related_name='survey_day')
    

class SurveyView(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user', on_delete=models.CASCADE, null=True)
    survey = models.ForeignKey(to=Survey, on_delete=models.CASCADE, verbose_name='Survey', null=True)
    
    class Meta:
        verbose_name = 'View'
        verbose_name_plural = 'Views'
        

class SurveyRadio(models.Model):
    survey = models.ForeignKey(to=Survey, on_delete=models.CASCADE, verbose_name='Survey')
    scores = models.IntegerField(verbose_name='scores', default=0)
    title = models.CharField(max_length=255, verbose_name="title")
    
    class Meta:
        verbose_name = 'Radio'
        verbose_name_plural = 'Radios'
        
    def __str__(self):
        return self.title


class SurveyVote(models.Model):
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='User')
    survey = models.ForeignKey(to=Survey, on_delete=models.CASCADE, verbose_name='Survey')
    option = models.ForeignKey(to=SurveyRadio, on_delete=models.CASCADE, verbose_name='Option', null=True)

@cleanup.ignore
class DraftSurvey(models.Model):
    preview = models.ImageField(
        verbose_name="Preview",
        upload_to=upload_to("uploads/surveys/drafts/previews"),
        null=True,
        blank=True,
    )
    size = models.IntegerField(blank=True, verbose_name='Size preview (KB)', null=True)
    title = models.CharField(
        verbose_name="Title", null=True, blank=True, max_length=255
    )
    description = models.TextField(verbose_name="Description", null=True, blank=True)
    content = models.TextField(verbose_name="Content", blank=True, null=True)
    language = models.CharField(max_length=255, verbose_name='Language', null=True, blank=True)
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE, verbose_name='Category', null=True, blank=True)
    subcategory = models.ForeignKey(to=Subcategory, on_delete=models.CASCADE, verbose_name='Subcategory', null=True, blank=True)
    blog = models.ForeignKey(to=Blog, on_delete=models.CASCADE)
    level_access = models.ForeignKey(to=LevelAccess, on_delete=models.CASCADE, verbose_name='Level access', null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )

    class Meta:
        verbose_name = "Draft"
        verbose_name_plural = "Drafts"

    def save(self, *args, **kwargs):
        if self.preview:
            self.size = self.preview.size
            self.preview = change_size(self.preview.path)
        if not self.blog.is_private and self.level_access:
            self.level_access = 0
        super(DraftSurvey, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class DraftSurveyTag(models.Model):
    title = models.CharField(
        verbose_name="Title", max_length=255, blank=False, null=False
    )
    draft_survey = models.ForeignKey(
        to=DraftSurvey, on_delete=models.CASCADE, verbose_name="Draft survey"
    )

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self):
        return self.title


class DraftSurveyRadio(models.Model):
    draft_survey = models.ForeignKey(
        to=DraftSurvey, on_delete=models.CASCADE, verbose_name="Draft survey"
    )
    title = models.CharField(max_length=255, verbose_name="title")

    class Meta:
        verbose_name = "Radio"
        verbose_name_plural = "Radios"

    def __str__(self):
        return self.title
