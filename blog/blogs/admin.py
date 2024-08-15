from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Blog


@admin.register(Blog)
class BlogAdmin(ModelAdmin):
    pass
