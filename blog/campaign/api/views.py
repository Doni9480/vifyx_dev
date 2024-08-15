from django.utils.timezone import now
import requests
from rest_framework import viewsets, permissions, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

# from transliterate import slugify
from django.utils.text import slugify
from campaign.models import Campaign, Task, UserTaskChecking
from configs.models import SiteConfiguration
from .serializers import (
    CampaignSerializer,
    NoneSerializer,
    TaskSerializer,
    UserTaskCheckingSerializer,
)
from django.shortcuts import get_object_or_404, redirect
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser


class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all()
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        if self.action == "list":
            return Campaign.objects.filter(is_active=True)
        elif self.action in ("retrieve", "set_status_enable", "set_status_disable"):
            pk = self.kwargs.get("pk")
            objects = Campaign.objects.filter(pk=pk)
            if len(objects) and objects.first().user.pk == self.request.user.pk:
                return objects
            return objects.filter(is_active=True)
        return Campaign.objects.filter(is_active=True)

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return CampaignSerializer
        elif self.action == "create_task":
            return TaskSerializer
        elif self.action == "list_task":
            return TaskSerializer
        return CampaignSerializer

    # def list(self, request, *args, **kwargs):
    #     return super().list(request, *args, **kwargs)

    def create(self, request, **kwargs):
        count_campaigns = Campaign.objects.filter(user=request.user).count()
        config = SiteConfiguration.get_solo()
        if count_campaigns >= config.limit_campaign:
            return Response(
                {"error": "Limit of campaigns reached."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if request.user.scores < int(request.data.get("prize_fund", 0)):
            return Response(
                {
                    "error": {
                        "prize_fund": [
                            f"You don't have enough points. Your score: {request.user.scores}"
                        ]
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(
                {"data": serializer.data, "success": "Campaign created successfully."},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    def partial_update(self, request, *args, **kwargs):
        if self.get_object().user != request.user:
            return Response(
                {"data": "You are not authorized to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().partial_update(request, *args, **kwargs)

    @action(detail=True, methods=["get"], url_path="<pk>/tasks")
    def list_task(self, request, pk=None):
        tasks_list = Task.objects.filter(campaign=pk)
        serializer = self.get_serializer(tasks_list, many=True)
        return Response(
            {"data": serializer.data, "success": "ok."}, status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=["patch"],
        url_path="<pk>/set_enable",
    )
    def set_status_enable(self, request, pk=None):
        campaign = self.get_object()
        if campaign.user != request.user:
            return Response(
                {"data": "You are not authorized to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        campaign.is_active = True
        campaign.save()
        return Response({"data": {"is_active": campaign.is_active}, "success": "ok."})

    @action(
        detail=True,
        methods=["patch"],
        url_path="<pk>/set_disable",
    )
    def set_status_disable(self, request, pk=None):
        campaign = self.get_object()
        if campaign.user != request.user:
            return Response(
                {"data": "You are not authorized to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        campaign.is_active = False
        campaign.save()
        return Response({"data": {"is_active": campaign.is_active}, "success": "ok."})


class TaskTypesViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        pk = self.kwargs.get("pk")
        if self.action == "list":
            return Task.objects.all()
        elif self.action == "retrieve":
            return Task.objects.filter(pk=pk)
        return Task.objects.all()

    def get_serializer_class(self):
        if self.action in ["create", "list", "retrieve", "partial_update"]:
            return TaskSerializer
        return NoneSerializer

    # def perform_create(self, serializer):
    #     serializer.save()

    def create(self, request):
        # campaign = self.get_object()
        print("*" * 100)
        print(request.data)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"data": serializer.data, "success": "ok."},
                status=status.HTTP_201_CREATED,
            )
        return Response({"data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        if self.get_object().user != request.user:
            return Response(
                {"data": "You are not authorized to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().partial_update(request, *args, **kwargs)

    @action(
        detail=True,
        methods=["patch"],
        url_path="<pk>/set_enable",
    )
    def set_status_enable(self, request, pk=None):
        task = self.get_object()
        if task.campaign.user != request.user:
            return Response(
                {"data": "You are not authorized to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        task.is_active = True
        task.save()
        return Response({"data": {"is_active": task.is_active}, "success": "ok."})

    @action(
        detail=True,
        methods=["patch"],
        url_path="<pk>/set_disable",
    )
    def set_status_disable(self, request, pk=None):
        task = self.get_object()
        if task.campaign.user != request.user:
            return Response(
                {"data": "You are not authorized to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        task.is_active = False
        task.save()
        return Response({"data": {"is_active": task.is_active}, "success": "ok."})


class TaskCheckingViewSet(viewsets.GenericViewSet):
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action == "task_running":
            return UserTaskCheckingSerializer
        return UserTaskCheckingSerializer

    @action(detail=True, methods=["post"], url_path="tasks/<pk>/run")
    def task_running(self, request, pk=None):
        object_set = UserTaskChecking.objects.filter(
            user=request.user, is_completed=False
        )
        if len(object_set) >= 1:
            return Response(
                {"data": None, "message": "You already have a task started"},
                status=status.HTTP_200_OK,
            )
        serializers = UserTaskCheckingSerializer(data=request.data)
        if serializers.is_valid():
            task_obj = get_object_or_404(Task, pk=pk)
            serializers.save(
                user=request.user, task=task_obj, points_awarded=task_obj.points_reward
            )
            return Response(
                {"data": serializers.data, "success": "ok.", "message": "Started!"},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"data": serializers.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=["get"], url_path="tasks/<pk>/check_visit")
    def check_task_visit(self, request, pk=None):
        task_obj = get_object_or_404(Task, pk=pk)
        if task_obj.task_type in [
            "telegram_subscription",
            "twitter_subscription",
            "website_visit",
            "wallet_connect",
            "twitter_connect",
            "periodic_bonus",
            "content_usage",
        ]:
            obj_set = UserTaskChecking.objects.filter(
                user=request.user, is_completed=False
            )
            if len(obj_set) == 1:
                obj_set[0].end_date = now()
                obj_set[0].is_completed = True
                obj_set[0].save()

            return redirect(task_obj.external_link)
        else:
            return redirect(task_obj.external_link)
        return Response(
            {"error": "Task type is not supported."}, status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=True,
        methods=["patch"],
        url_path="<pk>/receiving_an_award",
    )
    def receiving_an_award(self, request, pk=None):
        user_task_checking = UserTaskChecking.objects.filter(
            task=pk, is_completed=True
        ).first()
        if user_task_checking:
            user_task_checking.is_received = True
            user_task_checking.save()
            return Response(
                {
                    "data": {"is_received": user_task_checking.is_received},
                    "success": "ok.",
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Task not completed."},
                status=status.HTTP_404_NOT_FOUND,
            )
