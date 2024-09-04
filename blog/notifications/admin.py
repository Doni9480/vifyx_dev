from typing import Any
from django.contrib import admin
from unfold.admin import ModelAdmin
from django import forms
from notifications.models import Notification, SystemText
from users.models import User


class SystemTextForm(forms.ModelForm):
    class Meta:
        model = SystemText
        fields = '__all__'
        
    def clean(self, *args, **kwargs):
        english = self.cleaned_data.get('english')
        russian = self.cleaned_data.get('russian')
        title_eng = self.cleaned_data.get('title_eng')
        title_rus = self.cleaned_data.get('title_rus')
        text_eng = self.cleaned_data.get('text_eng')
        text_rus = self.cleaned_data.get('text_rus')
        if not (english or russian):
            raise forms.ValidationError({'english': 'Select at least one language option.'})
        if english and not (title_eng and text_eng):
            raise forms.ValidationError({'english': 'English fields must be required.'})
        if russian and not (title_rus and text_rus):
            raise forms.ValidationError({'russian': 'Russian fields must be required.'})
        return super(SystemTextForm, self).clean(*args, **kwargs)


@admin.register(SystemText)
class SystemTextAdmin(ModelAdmin):
    form = SystemTextForm
    
    def save_model(self, request, obj, form, change):
        obj.save()
        for user in User.objects.all():
            Notification.objects.create(user=user, system_text=obj)
                

@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    exclude = ('post', 'survey', 'album', 'quest', 'test', 'donate', 'contest', 
    'contest_post', 'contest_album', 'contest_quest', 'text', 'ban', 'unban', 'expiring_follow', 'user', 'is_read')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(system_text__isnull=True)