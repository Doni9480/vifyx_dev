from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.http import Http404
from albums.models import (
    Album, 
    Subcategory, 
    Category,
    AlbumDayView,
    AlbumView,
    AlbumWeekView,
    AlbumPhoto,
    DraftAlbum
)
from albums.api.serializers import (
    AlbumNoneSerializer,
    AlbumSerializer,
    SubcategorySerializer,
    AlbumIndexSerializer,
    AlbumShowSerializer,
    AlbumPhotoShowSerializer,
    DraftSerializer
)
from albums.api.utils import get_views_and_comments_to_albums
from blogs.models import Blog
from blogs.utils import get_filter_kwargs, get_obj_set, get_category
from users.utils import opening_access
from blog.utils import MyPagination, get_request_data, set_files_data, set_deleted_photos, set_language_to_user
from operator import attrgetter


class AlbumViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    permission_classes_by_action = dict.fromkeys(['list', 'retrieve'], [AllowAny])
    queryset = Album.objects.all()
    pagination_class = MyPagination
    
    def get_serializer_class(self):
        if self.action == 'create':
            return AlbumSerializer
        if self.action == 'retrieve':
            return AlbumShowSerializer
        return AlbumNoneSerializer
    
    def get_queryset(self):
        if self.action == 'get_subcategory':
            return Category.objects.all()
        return super().get_queryset()
    
    def get_permissions(self):
        try:
            # return permission_classes depending on `action`
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            # action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]
    
    def custom_get_object(self, **params):
        queryset = self.filter_queryset(self.get_queryset())

        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs, **params)

        self.check_object_permissions(self.request, obj)

        return obj
    
    def list(self, request, *args, **kwargs):
        request = set_language_to_user(request)
        filter_kwargs, subcategories, select_subcategories = get_category(get_filter_kwargs(request), request, 'albums')
        obj_set = get_obj_set(Album.level_access_objects.filter(**filter_kwargs), request.user)
        obj_set = sorted(obj_set, key=attrgetter('date'), reverse=True)
        
        albums = AlbumIndexSerializer(
            obj_set,
            many=True,
        ).data
        albums = get_views_and_comments_to_albums(albums)
        page = self.paginate_queryset(albums)
        return self.get_paginated_response(page)
    
    def retrieve(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        opening_access(instance, request.user, is_show=True)
        serializer_data = self.get_serializer(instance).data
        serializer_data['photos_set'] = AlbumPhotoShowSerializer(AlbumPhoto.objects.filter(album=instance), many=True).data
        if instance.is_not_subscribed:
            serializer_data['is_not_subscribed'] = True            
        return Response({"data": serializer_data})
    
    @transaction.atomic
    def create(self, request):
        _ = get_object_or_404(Blog, user=request.user.id, id=request.data.get('blog'))

        data = {}
        
        if request.user.is_authenticated and request.user.is_published_post:
            _data = set_files_data(get_request_data(request.data), request.FILES)

            # draft = DraftPost.objects.filter(user=request.user.id, blog=_data['blog'])
            # if not _data.get('preview', False):
            #     if draft and draft[0].preview:
            #         _data['preview'] = draft[0].preview
                    
            serializer = AlbumSerializer(data=_data, user=request.user)               
            if serializer.is_valid():
                album = serializer.save()
                
                # if draft:
                #     draft[0].delete()
                
                data['success'] = 'Successful created a new album.'
                data['slug'] = album.slug
            else:
                data = serializer.errors
        else:
            data['ban'] = 'You can\'t publish albums.'
        print(data)
        return Response(data)
    
    @transaction.atomic
    def partial_update(self, request, pk=None):
        data = {}
                    
        instance = self.custom_get_object(user=request.user)
        
        # language a not edit
        _data = set_files_data(set_deleted_photos(get_request_data(request.data)), request.FILES)
        print(_data)
        if _data.get('language', False):
            del _data['language']
                                
        serializer = AlbumSerializer(instance=instance, data=_data, partial=True, user=request.user)
            
        if serializer.is_valid():
            album = serializer.save()
            
            data['success'] = 'Successful updated a album.'
            data['slug'] = album.slug
        else:
            data = serializer.errors
            
        print(data)
        return Response(data)
    
    @action(detail=True, methods=["post"], url_path="<pk>/view/add")
    def add_view(self, request, pk=None):
        album = self.get_object()
        opening_access(album, request.user)
        views = [AlbumView, AlbumWeekView, AlbumDayView]
        for view in views:
            if not view.objects.filter(album=album).filter(user=request.user.id).first():
                view.objects.create(album=album, user=request.user)
        return Response({"success": "ok."})
    
    @action(detail=True, methods=["post"], url_path="<pk>/get_subcategory")
    def get_subcategory(self, request, pk=None):
        category = self.get_object()
        subcategories_set = Subcategory.objects.filter(category=category)
        subcategories = SubcategorySerializer(
            subcategories_set, many=True
        ).data
        return Response({"subcategories": subcategories})
    
    @action(detail=True, methods=["patch"], url_path="<pk>/hide_album")
    def hide_album(self, request, pk=None):
        data = {}

        album = self.get_object()
        if request.user == album.user:
            album.hide_to_user = True
        elif request.user.is_staff:
            album.hide_to_moderator = True
        else:
            raise Http404()

        album.save()

        data["success"] = "ok."

        return Response(data)

    @action(detail=True, methods=["patch"], url_path="<pk>/show_album")
    def show_album(self, request, pk=None):
        data = {}

        album = self.get_object()

        if request.user != album.user and not request.user.is_staff:
            raise Http404()

        if request.user == album.user and not album.hide_to_moderator:
            album.hide_to_user = False
        elif request.user.is_staff:
            album.hide_to_moderator = False
        else:
            data["ban"] = "You can't show the album"

        album.save()

        if not data.get("ban", False):
            data["success"] = "ok."

        return Response(data)
    
    def destroy(self, request, pk=None):
        instance = self.get_object()
        if instance.user != request.user:
            raise Http404()

        if request.method == "DELETE":
            data = {}
            
            photos = AlbumPhoto.objects.filter(album=instance)
            for photo in photos:
                photo.delete()

            instance.delete()

            data["success"] = "Successful deleted a survey."

            return Response(data)
        

class DraftAlbumViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = DraftAlbum.objects.all()

    def get_serializer_class(self):
        return DraftSerializer

    @transaction.atomic
    def create(self, request):
        data = {}
        
        _data = set_files_data(get_request_data(request.data), request.FILES)
        try:
            instance = get_object_or_404(
                DraftAlbum,
                user=request.user,
                blog=_data["blog"]
            )
            serializer = DraftSerializer(instance, data=set_deleted_photos(_data), partial=True, user=request.user)
        except Http404 as e:
            serializer = DraftSerializer(data=_data, user=request.user)
            
        if serializer.is_valid():
            serializer.save()
        else:
            data = serializer.errors

        if not data:
            data["success"] = "ok."

        print(data)
        return Response(data)