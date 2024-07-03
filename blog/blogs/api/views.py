from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.http import Http404

from blog.utils import check_recaptcha, add_months
from blogs.api.serializers import (
    BlogSerializer,
    PaySerializer,
    PostSerializer,
    SurveySerializer,
)
from blogs.models import Blog, LevelAccess, PaidFollow
from posts.api.utils import get_views_and_comments_to_posts
from posts.models import Post
from surveys.api.utils import get_views_and_comments_to_surveys
from surveys.models import Survey
from users.models import User, Percent

from itertools import chain


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
            data['slug'] = blog.slug
        else:
            data = serializer.errors
            
        return Response(data)

    @action(detail=True, methods=["get"], url_path="show/<str:slug>")
    def show(self, request, slug=None):
        blog = get_object_or_404(Blog, slug=slug)
        posts = get_views_and_comments_to_posts(
            PostSerializer(Post.objects.filter(blog=blog), many=True).data
        )
        surveys = get_views_and_comments_to_surveys(
            SurveySerializer(Survey.objects.filter(blog=blog), many=True).data
        )
        blog_list = posts + surveys

        paid_follow = PaidFollow.objects.filter(
            follower=request.user, blog=blog
        ).first()
        blog_data = []

        for e in blog_list:
            e["is_private"] = False
            if int(e["level_access"]) > 1:
                level_access = get_object_or_404(
                    LevelAccess, blog=blog, level=e["level_access"]
                )
                e["scores_to_follow"] = level_access.scores
                e["is_private"] = True

            e["is_followed"] = bool(
                paid_follow and paid_follow.blog_access_level.level >= e["level_access"]
            )
            blog_data.append(e)

        return Response({"data": blog_data})

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

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def pay(self, request, pk=None, level_access=None):
        blog = get_object_or_404(Blog, id=pk)
        if blog.user == request.user:
            raise Http404()

        level_access_obj = get_object_or_404(LevelAccess, blog=blog, level=level_access)
        paid_follow = PaidFollow.objects.filter(
            blog=blog, follower=request.user
        ).first()

        if paid_follow and int(level_access) <= paid_follow.blog_access_level.level:
            raise Http404()

        if paid_follow:
            paid_follow.delete()  # transaction is enabled. If error - paid_follow is not deleted

        data = {}
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            term = serializer.validated_data["term"]
            if term not in [1, 3, 6, 12]:
                term = 1

            user = request.user
            admin = User.objects.filter(is_superuser=True).first()
            user_blog = blog.user
            price = term * level_access_obj.scores

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
                    blog_access_level=level_access_obj,
                    count_months=term,
                    blog=blog,
                )
        else:
            data = serializer.errors

        if not data:
            data["success"] = "ok."
        return Response(data)

    @action(detail=True, methods=["delete"], url_path="delete_follow/<int:id>")
    @transaction.atomic
    def delete_follow(self, request, pk=None):
        blog = get_object_or_404(Blog, id=pk)
        paid_follow = get_object_or_404(PaidFollow, follower=request.user, blog=blog)
        paid_follow.delete()
        return Response({"success": "ok."})
