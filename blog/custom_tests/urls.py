from django.urls import path
from custom_tests.views import (
    list_tests,
    detail_test,
    test_create,
    test_edit,
    test_question_cerate,
    test_question_edit,
    test_run,
)


urlpatterns = [
    path("", list_tests, name="list_tests"),
    path("create/", test_create, name="test_create"),
    path("<slug:slug>/edit/", test_edit, name="test_edit"),
    path("<slug:slug>/", detail_test, name="detail_test"),
    path("<slug:slug>/run/", test_run, name="test_run"),
    path(
        "<slug:slug>/create_question/",
        test_question_cerate,
        name="test_create_question",
    ),
    path(
        "<slug:slug>/edit_question/<int:question_id>",
        test_question_edit,
        name="test_edit_question",
    ),
]
