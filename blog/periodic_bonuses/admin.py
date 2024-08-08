from django.contrib import admin
from .models import PeriodicBonuses, ReceivingPeriodicPoints


@admin.register(PeriodicBonuses)
class PeriodicBonusesAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "scores", "interval", "created_at")


@admin.register(ReceivingPeriodicPoints)
class ReceivingPeriodicPointsAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "periodic_bonus",
        "received_date",
        "is_received",
        "created_at",
    )
