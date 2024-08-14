from django.urls import path
from albums.views import (
    index,
    create,
    show,
    edit,
    draft_album_create
)


urlpatterns = [
    path('', index, name='index'),
    path('blog/<slug:slug>/create/', create, name='create'),
    path('show/<slug:slug>/', show, name="show"),
    path('edit/<slug:slug>/', edit, name="edit"),
    path('blog/<slug:slug>/draft/create/', draft_album_create, name="draft_album_create"),
]
