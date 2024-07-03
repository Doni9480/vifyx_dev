from django.db import transaction
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.urls import path, include

from rest_framework import viewsets, status, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser

from notifications.models import NotificationPost, NotificationSurvey
from notifications.api.seriailzers import (
    NotificationPostSerializer,
    NotificationSurveySerializer,
    NotificationPostShowSerializer,
    NotificationSurveyShowSerializer,
)
from users.models import User


class NotificationViewSet(
    # mixins.CreateModelMixin,
    # mixins.RetrieveModelMixin,
    # mixins.UpdateModelMixin,
    # mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def get_queryset(self):
        if self.action == "list":
            return NotificationPost.objects.filter(
                user=self.request.user.id, is_read=False
            )
        elif self.action in ["show_post", "show_survey", "read_it", "delete_all"]:
            return None  # These actions have custom queryset logic
        return NotificationPost.objects.none()  # Default case

    def get_serializer_class(self):
        if self.action == "show_post":
            return NotificationPostShowSerializer
        elif self.action == "show_survey":
            return NotificationSurveyShowSerializer
        elif self.action in ["list", "read_it", "delete_all"]:
            return NotificationPostSerializer  # Default serializer
        return NotificationPostSerializer

    def list(self, request, *args, **kwargs):
        notification_posts = NotificationPost.objects.filter(
            user=request.user.id, is_read=False
        )
        notification_surveys = NotificationSurvey.objects.filter(
            user=request.user.id, is_read=False
        )

        posts = [
            {
                **NotificationPostSerializer(notification_post.post).data,
                "namespace": "posts",
                "id": notification_post.id,
            }
            for notification_post in notification_posts
        ]

        surveys = [
            {
                **NotificationSurveySerializer(notification_survey.survey).data,
                "namespace": "surveys",
                "id": notification_survey.id,
            }
            for notification_survey in notification_surveys
        ]

        return Response({"data": surveys + posts})

    @action(detail=True, methods=["get"], url_path="show-post")
    def show_post(self, request, pk=None):
        notification_post = get_object_or_404(NotificationPost, id=pk)
        post = NotificationPostShowSerializer(notification_post.post).data
        post["user"] = User.objects.get(id=post["user"]).username
        return Response({"data": post})

    @action(detail=True, methods=["get"], url_path="show-survey")
    def show_survey(self, request, pk=None):
        notification_survey = get_object_or_404(NotificationSurvey, id=pk)
        survey = NotificationSurveyShowSerializer(notification_survey.survey).data
        survey["user"] = User.objects.get(id=survey["user"]).username
        return Response({"data": survey})

    @action(detail=False, methods=["post"], url_path="read-it")
    @transaction.atomic
    def read_it(self, request):
        notification_posts = NotificationPost.objects.filter(
            user=request.user.id, is_read=False
        )
        notification_surveys = NotificationSurvey.objects.filter(
            user=request.user.id, is_read=False
        )

        if not (notification_posts or notification_surveys):
            raise Http404()

        notification_posts.update(is_read=True)
        notification_surveys.update(is_read=True)

        return Response({"success": "ok."})

    @action(detail=False, methods=["delete"], url_path="delete-all")
    @transaction.atomic
    def delete_all(self, request):
        notification_posts = NotificationPost.objects.filter(user=request.user.id)
        notification_surveys = NotificationSurvey.objects.filter(user=request.user.id)

        if not (notification_posts or notification_surveys):
            raise Http404()

        notification_posts.delete()
        notification_surveys.delete()

        return Response({"success": "ok."})
