from rest_framework.routers import DefaultRouter
from django.urls import path, include
from notifications.api.views import NotificationViewSet

router = DefaultRouter()
router.register(r'', NotificationViewSet, basename='notifications')

urlpatterns = [
    # other urls
    path('', include(router.urls)),
]