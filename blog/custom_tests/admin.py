from django.contrib import admin
from unfold.admin import ModelAdmin
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
class TestAdmin(ModelAdmin):
    list_display = ("title", "user", "language", "hide_to_moderator", "created_at")
    list_display_links = ("title",)
    inlines = (QuestionInline,)


@admin.register(Question)
class QuestionAdmin(ModelAdmin):
    list_display = ("question", "test")
    list_filter = ("test__title",)
    inlines = (QuestionAnswerInline,)


@admin.register(QuestionAnswer)
class QuestionAnswerAdmin(ModelAdmin):
    list_display = ("variant", "question", "is_true")
    list_filter = ("question__question",)


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    pass


@admin.register(Subcategory)
class SubcategoryAdmin(ModelAdmin):
    pass
