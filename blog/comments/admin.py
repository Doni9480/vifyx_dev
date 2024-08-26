from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Comment, Answer


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    pass


@admin.register(Answer)
class AnswerAdmin(ModelAdmin):
    pass
