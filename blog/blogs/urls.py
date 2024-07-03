from django.urls import path

from blogs.views import create, show, edit


urlpatterns = [
    path('create/', create, name="create"),
    path('show/<slug:slug>/', show, name="show"),
    path('edit/<slug:slug>/', edit, name="edit"),
]
