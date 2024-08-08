from django.urls import path

from .views import get_periodic_bonus


urlpatterns = [
    path('<pk>', get_periodic_bonus, name='get_periodic_bonus'),
]
