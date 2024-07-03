from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin
from quests.models import Quest, QuestionQuest, QuestionQuestAnswer


@admin.register(Quest)
class QuestAdmin(admin.ModelAdmin):
    pass


@admin.register(QuestionQuest)
class QuestionQuestAdmin(DraggableMPTTAdmin):
    pass


@admin.register(QuestionQuestAnswer)
class QuestionQuestAnswerAdmin(DraggableMPTTAdmin):
    mptt_indent_field = "question"
