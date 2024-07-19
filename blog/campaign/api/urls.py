from django.urls import path, include
from blog.routers import CustomRouter
from rest_framework.routers import DefaultRouter
from .views import CampaignViewSet, TaskTypesViewSet, TaskCheckingViewSet

router = CustomRouter()
router.register(r'', CampaignViewSet, basename='campaign')
router.register(r'tasks', TaskTypesViewSet, basename='tasks')
router.register(r'', TaskCheckingViewSet, basename='tasks-checking')

urlpatterns = [
    path('', include(router.urls)),

]
