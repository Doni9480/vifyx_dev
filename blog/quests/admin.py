from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin
from quests.models import Quest, QuestionQuest, QuestionQuestAnswer, Subcategory, Category


@admin.register(Quest)
class QuestAdmin(admin.ModelAdmin):
    pass


@admin.register(QuestionQuest)
class QuestionQuestAdmin(DraggableMPTTAdmin):
    pass


@admin.register(QuestionQuestAnswer)
class QuestionQuestAnswerAdmin(DraggableMPTTAdmin):
    mptt_indent_field = "question"

admin.site.register(Category)
admin.site.register(Subcategory)