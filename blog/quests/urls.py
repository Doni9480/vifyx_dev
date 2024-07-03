from django.urls import path
from quests.views import (
    list_quests,
    detail_quest,
    quest_create,
    quest_edit,
    quest_question_cerate,
    quest_question_edit,
)


urlpatterns = [
    path("", list_quests, name="list_quests"),
    path("create/", quest_create, name="quest_create"),
    path("<slug:slug>/edit/", quest_edit, name="quest_edit"),
    path("<slug:slug>/", detail_quest, name="detail_quest"),
    path(
        "<slug:slug>/create_question/",
        quest_question_cerate,
        name="quest_cerate_question",
    ),
    path(
        "<slug:slug>/edit_question/<int:question_id>",
        quest_question_edit,
        name="quest_question_edit",
    ),
]
