from django.urls import path
from posts.views import (
    index,
    create, 
    show, 
    edit, 
    best_posts_mouth, 
    draft_post_create,
)


urlpatterns = [
    path('', index, name="index"),
    path('blog/<slug:slug>/create/', create, name='create'),
    path('show/<slug:slug>/', show, name="show"),
    path('edit/<slug:slug>/', edit, name="edit"),
    path('best_posts/30days/', best_posts_mouth, name="best_posts_mouth"),
    # draft
    path('blog/<slug:slug>/draft/create/', draft_post_create, name="draft_post_create"),
]