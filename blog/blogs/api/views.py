from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.http import Http404
from django.urls import reverse

from blog.utils import check_recaptcha, add_months
from blogs.api.serializers import (
    BlogSerializer,
    PaySerializer,
    PostSerializer,
    SurveySerializer,
    DonateSerializer,
    BlogShowSerializer,
    DonateShowSerializer,
    LevelFollowSerializer,
)
from blogs.models import Blog, LevelAccess, PaidFollow, Donate, BlogFollow
from blog.utils import get_request_data
from posts.api.utils import get_views_and_comments_to_posts
from posts.models import Post
from surveys.api.utils import get_views_and_comments_to_surveys
from surveys.models import Survey, SurveyRadio
from users.models import User, Percent
from notifications.models import NotificationBlog


class BlogViewSet(
    mixins.CreateModelMixin,
    # mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    # mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Blog.objects.all()
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action == "pay":
            return PaySerializer
        if self.action == "donate":
            return DonateSerializer
        return BlogSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        data = {}
        
        serializer = BlogSerializer(data=request.data, user=request.user.id)
        if serializer.is_valid():
            blog = serializer.save()
            blog.user = request.user
            blog.save()
            
            data['success'] = 'Successful created a new blog.'
            data['url'] = blog.slug
        else:
            data = serializer.errors
            
        return Response(data)

    @action(detail=True, methods=["get"], url_path=r'show/(?P<id>\d+)') # url_path=r'show/(?P<id>[^/.]+)'
    def show(self, request, id=None):
        blog = get_object_or_404(Blog, id=id)
        
        filter_kwargs = {'hide_to_user': False, 'hide_to_moderator': False, 'language': request.user.language, 'blog': blog}
        if request.user.language == 'any':
            del filter_kwargs['language']
        if request.user.is_staff:
            del filter_kwargs['hide_to_moderator']
            del filter_kwargs['hide_to_user']
            
        posts = get_views_and_comments_to_posts(
            PostSerializer(Post.objects.filter(**filter_kwargs), many=True).data
        )
        surveys = get_views_and_comments_to_surveys(
            SurveySerializer(Survey.objects.filter(**filter_kwargs), many=True).data
        )
        blog_list = posts + surveys

        return Response({"data": blog_list})

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        data = {}
        instance = get_object_or_404(Blog, user=request.user, id=kwargs.get("pk"))
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True,
            context={"user": request.user},
        )
        if serializer.is_valid():
            blog = serializer.save()
            data["success"] = "Successfully updated the blog."
            data["slug"] = blog.slug
        else:
            data = serializer.errors
        return Response(data)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        instance = get_object_or_404(Blog, id=kwargs.get("pk"), user=request.user)
        instance.delete()
        return Response({"success": "ok."})

    @action(detail=True, methods=["post"], url_path=r"pay/(?P<id>\d+)")
    @transaction.atomic
    def pay(self, request, id=None):
        blog = get_object_or_404(Blog, id=id)
        if blog.user == request.user:
            raise Http404()

        data = {}
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            level_follow_obj = get_object_or_404(LevelAccess, blog=blog, level=serializer.validated_data['level'])
            paid_follow = PaidFollow.objects.filter(
                blog=blog, follower=request.user
            ).first()

            if paid_follow and serializer.validated_data['level'] <= paid_follow.blog_access_level.level:
                raise Http404()

            if paid_follow:
                paid_follow.delete()  # transaction is enabled. If error - paid_follow is not deleted
            term = serializer.validated_data["term"]
            if term not in [1, 3, 6, 12]:
                term = 1

            user = request.user
            admin = User.objects.filter(is_superuser=True).first()
            user_blog = blog.user
            if user_blog == admin:
                user_blog = admin
            elif user == admin:
                user = admin
                
            price = term * level_follow_obj.scores

            if user.scores < price:
                data["error_scores"] = "You have fewer scores than you indicated."
            else:
                user.scores -= price
                user.save()

                percent = Percent.objects.first().percent / 100
                admin.scores += int(price * percent) or 1
                admin.save()

                user_blog.scores += int(price * (1 - percent)) or 1
                user_blog.save()

                date = add_months(timezone.now(), term)
                PaidFollow.objects.create(
                    date=date,
                    follower=user,
                    blog_access_level=level_follow_obj,
                    count_months=term,
                    blog=blog,
                )
        else:
            data = serializer.errors

        if not data:
            data["success"] = "ok."
        return Response(data)
    
    @action(detail=True, methods=['post'], url_path=r'donate/(?P<id>\d+)')
    @transaction.atomic
    def donate(self, request, id=None):
        blog = get_object_or_404(Blog, id=id)
        if request.user == blog.user:
            raise Http404()
        
        data = {}
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            amount = serializer.validated_data['amount']

            user = request.user
            admin = User.objects.filter(is_superuser=True).first()
            user_blog = blog.user
            if user_blog == admin:
                user_blog = admin
            elif user == admin:
                user = admin
            
            if user.scores < amount:
                data["error_scores"] = "You have fewer scores than you indicated."
            elif amount <= 0:
                data['error_scores'] = 'you cannot enter a negative value.'
            else:
                user.scores -= amount
                user.save()

                percent = Percent.objects.first().percent / 100
                admin.scores += int(amount * percent) or 1
                admin.save()
                
                user_blog.scores += int(amount * (1 - percent)) or 1
                user_blog.save()
                
                donate = serializer.save()
                donate.user = request.user
                donate.save()
        else:
            data = serializer.errors
            
        if not data:
            data["success"] = "ok."
        return Response(data)
    
    @action(detail=True, methods=["get"], url_path=r"donate_show/(?P<id>\d+)")
    def donate_show(self, request, id=None):
        donate = get_object_or_404(Donate, id=id)
        if request.user != donate.blog.user:
            raise Http404()
        return Response({"data": DonateShowSerializer(donate).data})

    @action(detail=True, methods=["delete"], url_path="delete_follow/<int:id>")
    @transaction.atomic
    def delete_follow(self, request, pk=None):
        blog = get_object_or_404(Blog, id=pk)
        paid_follow = get_object_or_404(PaidFollow, follower=request.user, blog=blog)
        paid_follow.delete()
        return Response({"success": "ok."})
    
    @action(detail=False, methods=["get"])
    def best_blogs(self, request):
        blog_models = Blog.objects.all()
        
        blog_data = []
        for blog in blog_models:
            blog = BlogShowSerializer(blog).data
            blog['scores'] = 0
            
            for post in Post.objects.filter(blog=blog['id']):
                blog['scores'] += post.scores
            for survey in Survey.objects.filter(blog=blog['id']):
                scores = 0
                options = SurveyRadio.objects.filter(survey=survey)
                for option in options:
                    scores += option.scores
                blog['scores'] += scores
            
            blog['user'] = User.objects.get(id=blog['user']).username
            
            blog_data.append(blog)

        return Response({"data": blog_data})
    
    @action(detail=False, methods=['post'], url_path='create_level_follow/<pk>')
    def create_level_follow(self, request, pk=None):
        blog = self.get_object()
        if blog.user != request.user or not blog.is_private:
            raise Http404()
        
        data = {}
        
        _data = get_request_data(request.data)
        _data['blog'] = blog.pk
        serializer = LevelFollowSerializer(data=_data)
        if serializer.is_valid():
            level_follow = serializer.save()
            data['slug'] = level_follow.blog.slug
            data['success'] = 'ok.'
        else:
            data = serializer.errors
        return Response(data)
    
    @action(detail=True, methods=["post"], url_path="<pk>/follow")
    @transaction.atomic
    def follow(self, request, pk=None):
        blog = self.get_object()
        if blog.user == request.user:
            raise Http404()

        BlogFollow.objects.create(follower=request.user, blog=blog)
        NotificationBlog.objects.create(blog=blog, follower=request.user, user=blog.user)
        return Response({"success": "ok."})

    @action(detail=True, methods=["post"], url_path="<pk>/unfollow")
    @transaction.atomic
    def unfollow(self, request, pk=None):
        blog = self.get_object()
        follow = BlogFollow.objects.filter(follower=request.user, blog=blog)
        if not follow or request.user == blog.user:
            raise Http404()

        follow.first().delete()
        
        notification_blog = NotificationBlog.objects.filter(blog=blog, follower=request.user.id, user=blog.user)
        notification_blog.first().delete()

        return Response({"success": "ok."})