from django.contrib import admin
from unfold.admin import ModelAdmin
from mptt.admin import DraggableMPTTAdmin
from quests.models import Quest, QuestionQuest, QuestionQuestAnswer, Subcategory, Category


@admin.register(Quest)
class QuestAdmin(ModelAdmin):
    pass


@admin.register(QuestionQuest)
class QuestionQuestAdmin(ModelAdmin, DraggableMPTTAdmin):
    pass


@admin.register(QuestionQuestAnswer)
class QuestionQuestAnswerAdmin(ModelAdmin):
    # mptt_indent_field = "question"
    pass

# admin.site.register(Category)
# admin.site.register(Subcategory)