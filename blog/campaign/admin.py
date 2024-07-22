from django.contrib import admin
from .models import UserTaskChecking, Task, Campaign

admin.site.register(Task)
admin.site.register(Campaign)

@admin.register(UserTaskChecking)
class UserTaskCheckAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'is_completed', 'points_awarded', 'start_date', 'end_date')
