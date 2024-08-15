from django.contrib import admin
from solo.admin import SingletonModelAdmin
from configs.models import SiteConfiguration
from unfold.admin import ModelAdmin

@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(ModelAdmin, SingletonModelAdmin):
    pass
