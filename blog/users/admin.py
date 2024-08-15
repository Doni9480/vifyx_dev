from django.contrib import admin
from users.models import TotalScore, User, Percent, Token, Percent_for_content
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group
from unfold.admin import ModelAdmin

admin.site.unregister(Group)

@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass

@admin.register(TotalScore)
class TotalScoreAdmin(ModelAdmin):
    pass


@admin.register(User)
class UserAdmin(ModelAdmin):
    pass


@admin.register(Percent)
class PercentAdmin(ModelAdmin):
    pass


@admin.register(Token)
class TokenAdmin(ModelAdmin):
    pass


@admin.register(Percent_for_content)
class Percent_for_contentAdmin(ModelAdmin):
    pass
