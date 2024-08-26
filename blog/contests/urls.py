from django.urls import path
from contests.views import index, show


urlpatterns = [
    path('', index, name="index"),
    path('show/<slug:slug>/', show, name="show"),
]
