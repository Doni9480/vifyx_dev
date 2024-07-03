from django.urls import path, include
from rest_framework.routers import DefaultRouter
from blog.routers import CustomRouter
from .views import DraftPostViewSet, PostViewSet

router = CustomRouter()
router.register(r'draft', DraftPostViewSet, basename='draft')
router.register(r'', PostViewSet, basename='post')


urlpatterns = [
    path('', include(router.urls)),
]
