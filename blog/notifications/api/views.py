from django.db import transaction
from django.shortcuts import get_object_or_404, get_list_or_404
from django.http import Http404
from django.urls import path, include

from rest_framework import viewsets, status, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser

from notifications.models import Notification, NotificationBlog
from notifications.api.seriailzers import (
    NotificationPostSerializer,
    NotificationPostShowSerializer,
    NotificationSurveySerializer,
    NotificationSurveyShowSerializer,
    NotificationDonateSerializer,
    NotificationDonateShowSerializer,
    NotificationNoneSerializer
)

from users.models import User

from blogs.models import Blog


class NotificationViewSet(
    # mixins.CreateModelMixin,
    # mixins.RetrieveModelMixin,
    # mixins.UpdateModelMixin,
    # mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = [IsAuthenticated]
    # parser_classes = [MultiPartParser]

    def get_queryset(self):
        if self.action == "list":
            return Notification.objects.filter(
                user=self.request.user.id, is_read=False
            )
        if self.action in ["show", "read_it", "delete_all"]:
            return Notification.objects.all()  # These actions have custom queryset logic
        return Notification.objects.none()  # Default case

    def get_serializer_class(self):
        if self.action == "show_post":
            return NotificationPostShowSerializer
        if self.action == "show_survey":
            return NotificationSurveyShowSerializer
        if self.action in ["list", "read_it", "delete_all"]:
            return NotificationPostSerializer  # Default serializer
        if self.action == 'get_notifications_blog':
            return NotificationNoneSerializer
        return NotificationPostSerializer

    def list(self, request, *args, **kwargs):
        notifications = Notification.objects.filter(
            user=request.user.id, is_read=False
        )
        
        data = [[], [], []]
        for notification in notifications:
            if notification.post:
                data[0].append({
                    **NotificationPostSerializer(notification.post).data,
                    'namespace': 'posts',
                })
            elif notification.survey:
                data[1].append({
                    **NotificationSurveySerializer(notification.survey).data,
                    'namespace': 'surveys',
                })
            elif notification.donate:
                data[2].append({
                    **NotificationDonateSerializer(notification.donate).data,
                    'namespace': 'donates',
                })

        return Response({"data": data})

    @action(detail=True, methods=["get"], url_path="show-post")
    def show_post(self, request, pk=None):
        notification_post = get_object_or_404(Notification, post=pk)
        post = NotificationPostShowSerializer(notification_post.post).data
        post["user"] = User.objects.get(id=post["user"]).username
        return Response({"data": post})

    @action(detail=True, methods=["get"], url_path="show-survey")
    def show_survey(self, request, pk=None):
        notification_survey = get_object_or_404(Notification, survey=pk)
        survey = NotificationSurveyShowSerializer(notification_survey.survey).data
        survey["user"] = User.objects.get(id=survey["user"]).username
        return Response({"data": survey})
    
    @action(detail=True, methods=["get"], url_path="show-donate")
    def show_donate(self, request, pk=None):
        notification_donate = get_object_or_404(Notification, donate=pk)
        donate = NotificationDonateShowSerializer(notification_donate.donate).data
        donate["user"] = User.objects.get(id=donate["user"]).username
        donate["blog"] = Blog.objects.get(id=donate["blog"]).title
        return Response({"data": donate})

    @action(detail=False, methods=["post"], url_path="read-it")
    @transaction.atomic
    def read_it(self, request):
        notifications = get_list_or_404(Notification, user=request.user.id)
        for notification in notifications: 
            notification.is_read = True
            notification.save()
            
        return Response({"success": "ok."})

    @action(detail=False, methods=["delete"], url_path="delete-all")
    @transaction.atomic
    def delete_all(self, request):
        notifications = get_list_or_404(Notification, user=request.user.id)
        for notification in notifications: notification.delete()
        return Response({"success": "ok."})
    
    @action(detail=False, methods=["post"], url_path=r"(?P<id>\d+)/get_notifications_blog")
    @transaction.atomic
    def get_notifications_blog(self, request, id=None):
        notification_blog = get_object_or_404(NotificationBlog, blog=id, follower=request.user)
        if request.data.get('get_notifications_blog', False):
            notification_blog.get_notifications_blog = True
        else:
            notification_blog.get_notifications_blog = False
        notification_blog.save()
        
        return Response({'success': 'ok.'})