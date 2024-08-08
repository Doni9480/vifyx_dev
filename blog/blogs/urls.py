from django.urls import path

from blogs.views import (
    create, 
    show, 
    edit, 
    donate,
    donate_show,
    create_level_follow
)


urlpatterns = [
    path('create/', create, name="create"),
    path('show/<slug:slug>/', show, name="show"),
    path('edit/<slug:slug>/', edit, name="edit"),
    path('<slug:slug>/donate/', donate, name="donate"),
    path('show/donate/<int:id>/', donate_show, name="donate_show"),
    path('<slug:slug>/create_level_follow/', create_level_follow, name="create_level_follow"),
]
