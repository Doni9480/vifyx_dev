from django.db import transaction
from django.shortcuts import get_object_or_404, get_list_or_404
from django.http import Http404

from rest_framework import viewsets, status, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser

from notifications.models import Notification, NotificationBlog
from notifications.api.seriailzers import (
    NotificationPostSerializer,
    NotificationSurveySerializer,
    NotificationTestSerializer,
    NotificationQuestSerializer,
    NotificationAlbumSerializer,
    NotificationDonateSerializer,
    NotificationNoneSerializer,
    NotificationContestSerializer,
    NotificationBanSerializer,
    NotificationUnbanSerializer,
    NotificationExpiringFollowSerializer,
    NotificationSystemTextSerializer,
    NotificationAnswerSerializer,
)


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
        if self.action in ["read_it", "delete_all"]:
            return Notification.objects.all()  # These actions have custom queryset logic
        return Notification.objects.none()  # Default case

    def get_serializer_class(self):
        if self.action in ["list", "read_it", "delete_all"]:
            return NotificationPostSerializer  # Default serializer
        if self.action == 'get_notifications_blog':
            return NotificationNoneSerializer
        return NotificationPostSerializer

    def list(self, request, *args, **kwargs):
        notifications = Notification.objects.filter(
            user=request.user
        )
        
        data = []
        for notification in notifications:
            E_DICTS = [
                {
                    'obj': notification.post,
                    'serializer': NotificationPostSerializer
                },
                {
                    'obj': notification.survey,
                    'serializer': NotificationSurveySerializer,
                },
                {
                    'obj': notification.test,
                    'serializer': NotificationTestSerializer,
                },
                {
                    'obj': notification.quest,
                    'serializer': NotificationQuestSerializer,
                },
                {
                    'obj': notification.album,
                    'serializer': NotificationAlbumSerializer,
                },
                {
                    'obj': notification.donate,
                    'serializer': NotificationDonateSerializer
                },
                {
                    'obj': notification.contest,
                    'serializer': NotificationContestSerializer
                },
                {
                    'obj': notification.ban,
                    'serializer': NotificationBanSerializer
                },
                {
                    'obj': notification.unban,
                    'serializer': NotificationUnbanSerializer
                },
                {
                    'obj': notification.expiring_follow,
                    'serializer': NotificationExpiringFollowSerializer
                },
                {
                    'obj': notification.system_text,
                    'serializer': NotificationSystemTextSerializer
                },
                {
                    'obj': notification.answer_notification,
                    'serializer': NotificationAnswerSerializer
                },
            ]
            for e_dict in E_DICTS:
                if e_dict['obj']:
                    data_res = {**e_dict['serializer'](e_dict['obj']).data}
                    data_res['date'] = notification.date
                    data.append(data_res)
        return Response({"data": data})

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
    
    @action(detail=False, methods=["post"], url_path=r"(?P<id>\d+)/get_notifications/(?P<namespace>[^/.]+)")
    @transaction.atomic
    def get_notifications(self, request, id=None, namespace=None):
        N_DICT = {
            'posts': 'get_notifications_post', 
            'albums': 'get_notifications_album', 
            'quests': 'get_notifications_quest',
            'answers': 'get_notifications_answer',
        }
        notification_blog = get_object_or_404(NotificationBlog, blog=id, follower=request.user)
        if request.data.get('get_notifications_element', False):
            setattr(notification_blog, N_DICT[namespace], True)
        else:
            setattr(notification_blog, N_DICT[namespace], False)
        notification_blog.save()
        return Response({'success': 'ok.'})