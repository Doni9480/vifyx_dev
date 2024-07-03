from django.urls import path

from blog.routers import CustomRouter
from blogs.api.views import BlogViewSet

router = CustomRouter()
router.register('', BlogViewSet, basename="blogs")
urlpatterns = router.urls
# urlpatterns = [
#     path('create/', create),
#     path('show/<slug:slug>/', show),
#     path('pay/<int:id>/<int:level_access>/', pay),
#     path('edit/<int:id>/', edit),
#     path('delete/<int:id>/', delete),
#     path('delete_follow/<int:id>/', delete_follow),
# ]
