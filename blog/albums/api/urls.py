from django.urls import path, include
from rest_framework.routers import DefaultRouter
from blog.routers import CustomRouter
from albums.api.views import AlbumViewSet, DraftAlbumViewSet

router = CustomRouter()
# router.register(r'draft', DraftPostViewSet, basename='draft')
router.register(r'', AlbumViewSet, basename='post')
router.register(r'draft', DraftAlbumViewSet, basename='draft') 


urlpatterns = [
    path('', include(router.urls)),
]