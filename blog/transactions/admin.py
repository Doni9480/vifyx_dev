from django.contrib import admin
from .models import Transactions

from unfold.admin import ModelAdmin


@admin.register(Transactions)
class TransactionsAdmin(ModelAdmin):
    list_display = ("from_user", "to_user", "amount", "custom_info", "status", "date")
    list_filter = ("from_user", "to_user")
    search_fields = ("from_user__username", "to_user__username")
    
    def custom_info(self, obj):
        return f"Type: {obj.info["translation"]["type"]}\n\
                Title: {obj.info["translation"]["title"]}"
    custom_info.short_description = "Info"
