from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db import transaction
from django.http import Http404
from django.http import QueryDict
from users.models import User, Percent
# from posts.api.serializers import DraftSerializer
# from posts.models import Draft


# from .serializers import DraftSerializer
# from posts.models import DraftPost

from .serializers import (
    PostSerializer,
    PostIndexSerializer,
    PostShowSerializer,
    PostShowNotBuySerializer,
    PostScoresSerializer,
    DraftSerializer,
    PostNoneSerializer,
    QuestionSerializer,
    PostTestDetailSerializer
)

from posts.models import (
    Post, 
    PostView, 
    PostTag, 
    DraftPost, 
    BuyPost, 
    Question, 
    PostRadio,
    PostVote,
)

from comments.models import Comment

from blog.decorators import recaptcha_checking
from blog.utils import custom_get_object_or_404 as get_object_or_404, get_request_data, set_language_to_user

from blogs.models import Blog

from users.models import User

from posts.utils import opening_access

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser


class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    permission_classes_by_action = dict.fromkeys(['list', 'show', 'add_view', 'get_test'], [AllowAny])
    queryset = Post.objects.all()
    # parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return PostShowSerializer
        elif self.action == "send_scores":
            return PostScoresSerializer
        if self.action in ['question_create', 'question_update']:
            return QuestionSerializer
        if self.action == 'get_test':
            return PostTestDetailSerializer
        if self.action not in ["add_view"]:
            return PostSerializer
        return PostNoneSerializer
    
    def get_queryset(self):
        if self.action in ['question_update', 'question_destroy']:
            return Question.objects.all()
        if self.action == 'send_scores_to_option':
            return PostRadio.objects.all()
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

    @swagger_auto_schema(
        operation_description="Создание", responses={201: PostShowSerializer}
    )
    @transaction.atomic
    def create(self, request):
        _ = get_object_or_404(Blog, user=request.user.id, id=request.data['blog'])

        data = {}
        
        if request.user.is_authenticated and request.user.is_published_post:
            _data = get_request_data(request.data)

            draft = DraftPost.objects.filter(user=request.user.id, blog=_data['blog'])
            if not _data.get('preview', False):
                if draft and draft[0].preview:
                    _data['preview'] = draft[0].preview
                    
            serializer = PostSerializer(data=_data, user=request.user)               
            if serializer.is_valid():
                post = serializer.save()
                
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
    def list(self, request):
        request = set_language_to_user(request)
        filter_kwargs = {'hide_to_user': False, 'hide_to_moderator': False, 'language': request.user.language}
        if request.user.language == 'any':
            del filter_kwargs['language']
        if request.user.is_staff:
            del filter_kwargs['hide_to_moderator']
            del filter_kwargs['hide_to_user']
            
        posts = PostIndexSerializer(
            Post.level_access_objects.filter(**filter_kwargs).order_by('-date')[:20], many=True
        ).data
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
    @action(detail=True, methods=["get"], url_path="show/<pk>")
    def show(self, request, pk=None):
        request = set_language_to_user(request)
        post_model = self.get_object()
        if opening_access(post_model, request.user):
            raise Http404()
        
        if post_model.is_paid and not BuyPost.objects.filter(user=request.user.id, post=post_model):
            post = PostShowNotBuySerializer(post_model).data
            post['content'] = "This post is paid"
        else:
            post = PostShowSerializer(post_model).data
            
            tags = PostTag.objects.filter(post_id=post['id'])
            post['tags'] = []   
            for tag in tags:
                post['tags'].append(tag.title)

        if post['language'] == "2":
            post['language'] = "Russian"
        else:
            post['language'] = "English"
            
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
            post = self.get_object()
            if opening_access(post, request.user):
                raise Http404()
            
            view = PostView.objects.filter(post=post).filter(user=request.user.id)
            if not view:
                PostView.objects.create(
                    post=post,
                    user=request.user.id
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
                    
        instance = self.custom_get_object(user=request.user)
        
        # language a not edit
        _data = get_request_data(request.data)
        if _data.get('language', False):
            del _data['language']
                                
        serializer = PostSerializer(instance=instance, data=_data, partial=True, user=request.user)
            
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
        instance = self.get_object()
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
        
        post = self.get_object()
        if opening_access(post, request.user):
            raise Http404()
        
        serializer = PostScoresSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            admin = User.objects.filter(is_superuser=True).first()
            if user == admin:
                user = admin
            
            scores = int(serializer.validated_data['scores'])

            if user.scores < scores:
                data['error_scores'] = 'you have fewer scores than you indicated.'
            elif scores <= 0:
                data['error_scores'] = 'you cannot enter a negative value.'
            else:            
                user.scores -= scores
                user.save()
    
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
    
    @action(detail=True, methods=["post"], url_path="send_scores_to_option/<pk>")
    @transaction.atomic
    def send_scores_to_option(self, request, pk=None):
        data = {}

        option = self.get_object()
        if opening_access(option.post, request.user):
            raise Http404()

        if (
            (PostVote.objects.filter(user=request.user.id, post=option.post))
            or (option.post.hide_to_moderator or option.post.hide_to_user and not request.user.is_staff)
        ):
            raise Http404()

        serializer = PostScoresSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            admin  = User.objects.filter(is_superuser=True).first()
            if user == admin:
                user = admin

            scores = int(serializer.validated_data["scores"])

            if user.scores <= scores:
                data["error_scores"] = "you have fewer scores than you indicated."
            elif scores <= 0:
                data["error_scores"] = "you cannot enter a negative value."
            else:
                user.scores -= scores
                user.save()
                
                percent = Percent.objects.all()[0].percent / 100
                admin.scores += int(scores * percent) or 1
                admin.save()

                reverse_percent = 1 - Percent.objects.all()[0].percent / 100
                scores = int(scores * reverse_percent) or 1

                option.scores += scores
                option.save()

                # user is vote
                PostVote.objects.create(user=user, post=option.post, option=option)

                data["success"] = "ok."
                data["scores"] = option.scores
        else:
            data = serializer.errors

        return Response(data)

    @swagger_auto_schema(operation_description="Создание", responses={200: None})
    @transaction.atomic
    @action(detail=True, methods=["patch"], url_path="<pk>/hide_post")
    def hide_post(self, request, pk=None):
        data = {}

        post = self.get_object()
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

        post = self.get_object()

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
    
    @transaction.atomic
    @action(detail=True, methods=["post"], url_path="buy/<pk>")
    def buy(self, request, pk=None, username=None):
        post = self.custom_get_object(is_paid=True)
        if opening_access(post, request.user) or BuyPost.objects.filter(user=request.user.id, post=post):
            raise Http404()
        
        data = {}
        
        user = request.user
        admin = User.objects.filter(is_superuser=True).first()
        user_post = post.user
        if user_post == admin:
            user_post = admin
        elif user == admin:
            user = admin
            
        if request.user.scores < post.amount:
            data["error_scores"] = "you have fewer scores than you indicated."
        else:
            amount = post.amount
            user.scores -= amount
            user.save()
            
            percent = Percent.objects.first().percent / 100
            admin.scores += int(amount * percent) or 1
            admin.save()

            user_post.scores += int(amount * (1 - percent)) or 1
            user_post.save()
            
            BuyPost.objects.create(post=post, scores=amount, user=user)
            
        if not data:
            data['success'] = 'ok.'
        return Response(data)

    @action(detail=True, methods=["post"], url_path="question/create")
    @transaction.atomic
    def question_create(self, request, *args, **kwargs):
        data = {}
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            valid = True
            err = None
            if valid:
                data["success"] = "ok."
                data["data"] = serializer.data
                return Response(data, status=status.HTTP_201_CREATED)
            else:
                data["data"] = err
        else:
            data["data"] = serializer.errors
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=["patch"], url_path="question/<pk>/update")
    @transaction.atomic
    def question_update(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        if not request.user == instance.post.user:
            raise Http404()
        
        serializer = self.get_serializer(instance=instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "success": "ok."})
        else:
            return Response(
                {"data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )
            
    @action(detail=True, methods=["delete"], url_path="question/<pk>/delete")
    def question_destroy(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        if not request.user == instance.post.user:
            raise Http404()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=["get"], url_path="test_run/<pk>")
    def get_test(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        request = set_language_to_user(request)
        if opening_access(instance, request.user):
            raise Http404()
        serializer = self.get_serializer(instance)
        return Response({"data": serializer.data})

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
        
        _data = get_request_data(request.data)
        try:
            instance = get_object_or_404(
                DraftPost,
                user=request.user,
                blog=_data["blog"]
            )
            serializer = DraftSerializer(instance, data=_data, partial=True, user=request.user)
        except Http404 as e:
            serializer = DraftSerializer(data=_data, user=request.user)
            
        if serializer.is_valid():
            serializer.save()
        else:
            data = serializer.errors

        if not data:
            data["success"] = "ok."

        return Response(data)
