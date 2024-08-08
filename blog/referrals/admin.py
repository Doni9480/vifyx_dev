from django.contrib import admin
from .models import Referral, BonusCoefficients


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ("referral_user", "code", "tasks_completed", "created_at")


@admin.register(BonusCoefficients)
class BonusCoefficientsAdmin(admin.ModelAdmin):
    list_display = ("from_num", "to_num", "coefficient")