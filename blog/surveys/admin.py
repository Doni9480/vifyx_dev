from django.contrib import admin
from unfold.admin import ModelAdmin
from surveys.models import (
    Survey,
    SurveyTag,
    SurveyRadio,
    SurveyView,
    SurveyVote,
    Category,
    Subcategory,
)


@admin.register(Survey)
class SurveyAdmin(ModelAdmin):
    pass


@admin.register(SurveyTag)
class SurveyTagAdmin(ModelAdmin):
    pass


@admin.register(SurveyRadio)
class SurveyRadioAdmin(ModelAdmin):
    pass


@admin.register(SurveyView)
class SurveyViewAdmin(ModelAdmin):
    pass


@admin.register(SurveyVote)
class SurveyVoteAdmin(ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    pass


@admin.register(Subcategory)
class SubcategoryAdmin(ModelAdmin):
    pass
