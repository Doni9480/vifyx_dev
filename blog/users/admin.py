from django.contrib import admin
from users.models import TotalScore, User, Percent, Token, Percent_for_content
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group
from django.urls import path  # Импорт path
from django.utils.html import format_html
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.http import HttpRequest
from unfold.admin import ModelAdmin
from unfold.decorators import action

admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


@admin.register(TotalScore)
class TotalScoreAdmin(ModelAdmin):
    pass


@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = (
        "id",
        "username",
        "telegram_wallet",
        "completed_tasks",
        "points_for_completed_tasks",
        # "is_active",
        "users_posts",
        "user_transactions",
        "list_buttons",
    )
    search_fields = ("id", "username", "telegram_wallet")
    # list_editable =
    list_display_links = ("username",)
    # actions_detail = ["change_detail_action_block"]
    # list_editable = ( "is_active", )
    # actions_row = ["lock_or_unlock_user_row_action", "moderators_rights"]

    # is_active.

    def list_buttons(self, obj):
        all_btn = ""
        btn_template = """<button class="bg-primary-600 block border border-transparent font-medium px-2 py-1 rounded-md text-white w-full lg:w-auto" data-pk="{pk}" data-current-status="{status}" data-type="{handler_type}">{text}</button>"""
        Group.objects.get_or_create(name="Moderator")
        if obj.groups.filter(name="Moderator").exists():
            all_btn += btn_template.format(
                pk=obj.pk,
                status=True,
                handler_type="moderator",
                text="Moderator's rights: yes",
            )
        else:
            all_btn += btn_template.format(
                pk=obj.pk,
                status=False,
                handler_type="moderator",
                text="Moderator's rights: no",
            )

        if obj.is_active:
            all_btn += btn_template.format(
                pk=obj.pk,
                status=obj.is_active,
                handler_type="user_status",
                text="Unlocked",
            )
        else:
            all_btn += btn_template.format(
                pk=obj.pk,
                status=obj.is_active,
                handler_type="user_status",
                text="Locked",
            )

        block_div = (
            f'<div class="lg:w-auto" style="display: flex; gap:5px;">{all_btn}</div>'
        )
        return format_html(block_div)

    list_buttons.short_description = "Actions"

    def completed_tasks(self, obj):
        return obj.number_of_completed_tasks()

    completed_tasks.short_description = "Completed tasks"

    def points_for_completed_tasks(self, obj):
        return obj.number_of_points_for_completed_tasks()

    points_for_completed_tasks.short_description = "Points for completed tasks"

    def user_transactions(self, obj):
        tag_link = f'<a href="/admin/transactions/transactions/?q={obj.username}">User transactions</a>'
        block_div = f"<div>{tag_link}</div>"
        return format_html(block_div)
    user_transactions.short_description = "User transactions"
    
    def users_posts(self, obj):
        tag_link = f'<a href="/admin/posts/post/?user__id__exact={obj.pk}">Posts</a>'
        block_div = f"<div>{tag_link}</div>"
        return format_html(block_div)
    users_posts.short_description = "User's posts"

    class Meta:
        js = ("js/admin/custom/custom_user.js",)


@admin.register(Percent)
class PercentAdmin(ModelAdmin):
    pass


@admin.register(Token)
class TokenAdmin(ModelAdmin):
    pass


@admin.register(Percent_for_content)
class Percent_for_contentAdmin(ModelAdmin):
    pass
