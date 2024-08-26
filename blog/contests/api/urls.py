from django.urls import path

from blog.routers import CustomRouter
from contests.api.views import ContestViewSet

router = CustomRouter()
router.register('', ContestViewSet, basename="contests")
urlpatterns = router.urls