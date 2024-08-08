from blog.routers import CustomRouter
from .views import ReceivingPeriodicPointsViewSet

router = CustomRouter()
router.register(r"", ReceivingPeriodicPointsViewSet, basename="periodic_bonuses")

urlpatterns = router.urls
