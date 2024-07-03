from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.http import Http404
from posts.models import DraftPost
from users.models import User, Percent
# from posts.api.serializers import DraftSerializer
# from posts.models import Draft


# from .serializers import DraftSerializer
# from posts.models import DraftPost

from .serializers import (
    PostSerializer,
    PostIndexSerializer,
    PostShowSerializer,
    PostScoresSerializer,
    DraftSerializer,
    PostNoneSerializer,
)

from posts.models import Post, PostView, PostTag, DraftPost, DraftPostTag

from comments.models import Comment

from blog.decorators import recaptcha_checking

from blogs.models import Blog

from users.models import User

from posts.utils import opening_access

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser


class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Post.objects.all()
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return PostShowSerializer
        elif self.action == "send_scores":
            return PostScoresSerializer
        if self.action not in ["add_view"]:
            return PostSerializer
        else:
            return PostNoneSerializer

    @swagger_auto_schema(
        operation_description="Создание", responses={201: PostShowSerializer}
    )
    def create(self, request):
        _ = get_object_or_404(Blog, user=request.user.id, id=request.data['blog'])
        
        data = {}
        
        if request.user.is_authenticated and request.user.is_published_post:
            request.data._mutable = True

            request.data['language'] = request.user.language

            draft = DraftPost.objects.filter(user=request.user.id, blog=request.data['blog'])
            if not request.data.get('preview', False):
                if draft and draft[0].preview:
                    request.data['preview'] = draft[0].preview

            request.data._mutable = False
                    
            serializer = PostSerializer(data=request.data, user=request.user.id)               
            if serializer.is_valid():
            
                post = serializer.save()
                        
                post.user = request.user
                post.save()
                
                if draft:
                    draft[0].delete()
                
                data['success'] = 'Successful created a new post.'
                data['slug'] = post.slug
            else:
                data = serializer.errors
        else:
            data['ban'] = 'You can\'t publish posts.'
        
        return Response(data)

    @swagger_auto_schema(
        operation_description="Получение данных!",
        # request_body=PostIndexSerializer,
        responses={200: PostIndexSerializer},
    )
    @action(detail=False, methods=["get"])
    def index(self, request):
        posts = PostIndexSerializer(Post.level_access_objects.filter(language=request.user.language), many=True).data
        for post in posts:
            post['user'] = User.objects.get(id=post['user']).username
            post['count_views'] = PostView.objects.filter(post_id=post['id']).count()
            post['count_comments'] = Comment.objects.filter(post_id=post['id']).count()
            
            if post['language'] == "2":
                post['language'] = "Russian"
            else:
                post['language'] = "English" 
        
        return Response({'data': posts})

    @swagger_auto_schema(
        operation_description="Получение данных!",
        # request_body=PostShowSerializer,
        responses={200: PostShowSerializer},
    )
    @action(detail=True, methods=["get"])
    def show(self, request, pk=None):
        post_model = get_object_or_404(Post.objects, id=pk)
        if opening_access(post_model, request.user.id):
            raise Http404()
        
        post = PostShowSerializer(post_model).data

        if post['language'] == "2":
            post['language'] = "Russian"
        else:
            post['language'] = "English"
            
        tags = PostTag.objects.filter(post_id=post['id'])
        post['tags'] = []   
        for tag in tags:
            post['tags'].append(tag.title)
            
        post['user'] = User.objects.get(id=post['user']).username
        
        return Response({'data': post})

    # @swagger_auto_schema(
    #     operation_description="Создание",
    #     request_body=openapi.Schema(
    #         type=openapi.TYPE_OBJECT,
    #         properties={}
    #     ),
    #     responses={200: None}
    # )
    @action(detail=True, methods=["post"], url_path="<pk>/view/add")
    def add_view(self, request, pk=None):
        if request.user.is_authenticated:
            post = get_object_or_404(Post.objects, id=pk)
            if opening_access(post, request.user):
                raise Http404()
            
            view = PostView.objects.filter(post=post).filter(user=request.user)
            if not view:
                PostView.objects.create(
                    post=post,
                    user=request.user
                )
            
        return Response({'success': 'ok.'})

    @swagger_auto_schema(
        operation_description="Изменение данных",
        request_body=PostSerializer,
        responses={200: PostSerializer},
    )
    @transaction.atomic
    def partial_update(self, request, pk=None):
        data = {}
                    
        instance = get_object_or_404(Post.objects, id=pk, user=request.user.id)
        # language a not edit
        request.data._mutable = True
        if request.data.get('language', False):
            del request.data['language']
        request.data._mutable = False
                                
        serializer = PostSerializer(instance=instance, data=request.data, partial=True, user=request.user.id)
            
        if serializer.is_valid():
            post = serializer.save()
            
            data['success'] = 'Successful updated a post.'
            data['slug'] = post.slug
        else:
            data = serializer.errors
            
        return Response(data)

    @swagger_auto_schema(
        operation_description="Удаление", responses={204: "No Content"}
    )
    @transaction.atomic
    def destroy(self, request, pk=None):
        instance = get_object_or_404(Post.objects, id=pk)
        if instance.user != request.user:
            raise Http404()
        
        data = {}
        
        tags = PostTag.objects.filter(post=instance)
        for tag in tags:
            tag.delete()
                
        instance.delete()
        
        data['success'] = 'Successful deleted a post.'
        
        return Response(data)

    # @swagger_auto_schema(
    #     operation_description="Создание",
    #     request_body=ScoresSerializer,
    #     responses={200: ScoresSerializer},
    # )
    @transaction.atomic
    @action(detail=True, methods=["post"], url_path="<pk>/send_scores")
    def send_scores(self, request, pk=None):
        data = {}
        
        post = get_object_or_404(Post.objects, id=pk)
        if opening_access(post, request.user):
            raise Http404()
        
        serializer = PostScoresSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            
            scores = int(serializer.validated_data['scores'])
            user.scores -= scores
            if user.scores <= 0:
                data['error_scores'] = 'you have fewer scores than you indicated.'
            elif scores <= 0:
                data['error_scores'] = 'you cannot enter a negative value.'
            else:
                user.save()
            
                admin = User.objects.filter(is_superuser=True)[0]
                percent = Percent.objects.all()[0].percent / 100
                admin.scores += int(scores * percent) or 1
                admin.save()
                
                reverse_percent = 1 - Percent.objects.all()[0].percent / 100
                scores = int(scores * reverse_percent) or 1

                post.scores += scores
                post.mouth_scores += scores
                post.save()
                
                data['success'] = 'ok.'
                data['scores'] = post.scores
        else:
            data = serializer.errors
            
        return Response(data)

    @swagger_auto_schema(operation_description="Создание", responses={200: None})
    @transaction.atomic
    @action(detail=True, methods=["patch"], url_path="<pk>/hide_post")
    def hide_post(self, request, pk=None):
        data = {}

        post = get_object_or_404(Post.objects, id=pk)
        if request.user == post.user:
            post.hide_to_user = True
        elif request.user.is_staff:
            post.hide_to_moderator = True
        else:
            raise Http404()
        post.save()
        data['success'] = 'ok.'

        return Response(data)

    @swagger_auto_schema(operation_description="Создание", responses={200: None})
    @transaction.atomic
    @action(detail=True, methods=["patch"], url_path="<pk>/show_post")
    def show_post(self, request, pk=None):
        data = {}

        post = get_object_or_404(Post.objects, id=pk)

        if request.user != post.user and not request.user.is_staff:
            raise Http404()

        if request.user == post.user and not post.hide_to_moderator:
            post.hide_to_user = False
        elif request.user.is_staff:
            post.hide_to_moderator = False
        else:
            data['ban'] = 'You can\'t show the post'
        post.save()
        if not data.get('ban', False):
            data['success'] = 'ok.'

        return Response(data)


# draft_post
class DraftPostViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = DraftPost.objects.all()
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return DraftSerializer if "post" in self.request.data else DraftSerializer
        return DraftSerializer  # Default serializer

    @swagger_auto_schema(
        operation_description="Создание",
        request_body=DraftSerializer,
        responses={201: DraftSerializer},
    )
    @transaction.atomic
    def create(self, request):
        data = {}
        instance = DraftPost.objects.filter(
            user=request.user.id, blog=request.data["blog"]
        )
        if not instance:
            serializer = DraftSerializer(data=request.data)

            if serializer.is_valid():
                draft = serializer.save()

                draft.user = request.user
                draft.save()
            else:
                data = serializer.errors
        else:
            instance = instance[0]
            serializer = DraftSerializer(instance, data=request.data, partial=True)

            if serializer.is_valid():
                draft = serializer.save()
            else:
                data = serializer.errors

        if not data:
            data["success"] = "ok."

        return Response(data)
