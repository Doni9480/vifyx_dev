from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import UserTaskChecking, Task, Campaign


@admin.register(Task)
class TaskAdmin(ModelAdmin):
    pass


@admin.register(Campaign)
class CampaignAdmin(ModelAdmin):
    pass


@admin.register(UserTaskChecking)
class UserTaskCheckAdmin(ModelAdmin):
    list_display = (
        "task",
        "user",
        "is_completed",
        "points_awarded",
        "start_date",
        "end_date",
    )
