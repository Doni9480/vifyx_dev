from django.urls import re_path, path, include

from blog.routers import CustomRouter
from .views import (
    # CreateQuestView,
    # QuestDetailView,
    # QuestEditView,
    # QuestDeleteView,
    # QuestsListView,
    # QuestVisibilityView,
    # QuestQuestionEditView,
    # QuestQuestionCreateView,
    # QuestQuestionDeleteView,
    QuestViewSet,
)

router = CustomRouter()
router.register(r'', QuestViewSet, basename='quests')

urlpatterns = [
    path('', include(router.urls)),
]


# urlpatterns = [
#     path("", QuestsListView.as_view({'get': 'list'}), name="api_quest_list"),
#     path("<pk>", QuestDetailView.as_view({'get': 'list'}), name="api_quest_detail"),
#     path("<pk>/edit/", QuestEditView.as_view({'put': 'update'}), name="api_quest_edit"),
#     path("<pk>/delete/", QuestDeleteView.as_view({'delete': 'destroy'}), name="api_quest_delete"),
#     path("create/", CreateQuestView.as_view({'post': 'create'}), name="api_quest_create"),
#     path("<pk>/visibility/", QuestVisibilityView.as_view({'put': 'update'}), name="api_quest_visibility"),
#     path(
#         "<pk>/question/cerate/",
#         QuestQuestionCreateView.as_view({'post': 'create'}),
#         name="api_quest_question_cerate",
#     ),
#     path(
#         "question/<pk>/edit/",
#         QuestQuestionEditView.as_view({'put': 'update'}),
#         name="api_quest_question_edit",
#     ),
#     path(
#         "question/<pk>/delete/",
#         QuestQuestionDeleteView.as_view({'delete': 'destroy'}),
#         name="api_quest_question_delete",
#     ),
# ]