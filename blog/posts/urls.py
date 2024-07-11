from django.urls import path
from posts.views import (
    create, 
    show, 
    edit, 
    best_posts_mouth, 
    draft_post_create,
    post_question_create,
    post_question_edit,
    test_run
)


urlpatterns = [
    path('blog/<slug:slug>/create/', create, name='create'),
    path('show/<slug:slug>/', show, name="show"),
    path("<slug:slug>/run/", test_run, name="test_run"),
    path('edit/<slug:slug>/', edit, name="edit"),
    path('best_posts/30days/', best_posts_mouth, name="best_posts_mouth"),
    # draft
    path('blog/<slug:slug>/draft/create/', draft_post_create, name="draft_post_create"),
    path(
        "blog/<slug:slug>/create_question/",
        post_question_create,
        name="post_create_question",
    ),
    path(
        "<slug:slug>/edit_question/<int:question_id>",
        post_question_edit,
        name="post_edit_question",
    ),
]