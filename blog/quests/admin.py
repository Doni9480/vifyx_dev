from django.contrib import admin
from unfold.admin import ModelAdmin
from mptt.admin import DraggableMPTTAdmin
from quests.models import Quest, QuestionQuest, QuestionQuestAnswer, Subcategory, Category, QuestView


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


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    pass


@admin.register(Subcategory)
class SubcategoryAdmin(ModelAdmin):
    pass

@admin.register(QuestView)
class QuestViewAdmin(ModelAdmin):
    pass