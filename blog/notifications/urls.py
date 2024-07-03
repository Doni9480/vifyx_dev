from django.urls import path

from notifications.views import index


urlpatterns = [
    path('', index, name='index'),
]
