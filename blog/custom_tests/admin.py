from django.contrib import admin
from .models import Test, Question, QuestionAnswer, Category, Subcategory


class QuestionAnswerInline(admin.TabularInline):
    model = QuestionAnswer
    extra = 1
    min_num = 2


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    min_num = 2


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "language", "hide_to_moderator", "created_at")
    list_display_links = ("title",)
    inlines = (QuestionInline,)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("question", "test")
    list_filter = ("test__title",)
    inlines = (QuestionAnswerInline,)


@admin.register(QuestionAnswer)
class QuestionAnswerAdmin(admin.ModelAdmin):
    list_display = ("variant", "question", "is_true")
    list_filter = ("question__question",)

admin.site.register(Category)
admin.site.register(Subcategory)