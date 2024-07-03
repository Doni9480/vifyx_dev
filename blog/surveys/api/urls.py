from django.urls import path, include
# from rest_framework.routers import DefaultRouter
from .views import SurveyViewSet, DraftSurveyViewSet
from blog.routers import CustomRouter

router = CustomRouter()
router.register(r'', SurveyViewSet, basename='survey')
router.register(r'draft', DraftSurveyViewSet, basename='survey_draft')

urlpatterns = [
    path('', include(router.urls)),
]
