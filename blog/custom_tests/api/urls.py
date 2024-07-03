from django.urls import path, include
from .views import (
     TestViewSet,
)
from blog.routers import CustomRouter

test_routers = CustomRouter()
test_routers.register(r'', TestViewSet, basename='custom_test')

urlpatterns = [
    *test_routers.urls
]