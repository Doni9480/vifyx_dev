from django.utils.timezone import now
from rest_framework import viewsets, permissions, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
# from transliterate import slugify
from django.utils.text import slugify
from campaign.models import Campaign, Task, UserTaskChecking
from .serializers import CampaignSerializer, TaskSerializer, UserTaskCheckingSerializer
from django.shortcuts import get_object_or_404, redirect
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from constance import config


class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all()
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        if self.action == "list":
            return Campaign.objects.all()
        elif self.action == "retrieve":
            pk = self.kwargs.get("pk")
            return Campaign.objects.filter(pk=pk)
        return Campaign.objects.all()

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return CampaignSerializer
        elif self.action == "create_task":
            return TaskSerializer
        elif self.action == "list_task":
            return TaskSerializer
        return CampaignSerializer

    def create(self, request, **kwargs):
        count_campaigns = Campaign.objects.filter(user=request.user).count()
        if count_campaigns >= config.LIMIT_CAMPAIGN:
            return Response(
                {"data": "Limit of campaigns reached."}, status=status.HTTP_403_FORBIDDEN
            )
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(
                {"data": serializer.data, "success": "Campaign created successfully."},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )
        
    # def partial_update(self, request, *args, **kwargs):
    #     campaign = self.get_object()
    #     if campaign.user != request.user:
    #     serializer = CampaignSerializer(campaign, data=request.data, partial=True)
    #     if serializer.is_valid():
    #         name = serializer.validated_data.get("name", None)
    #         serializer.save(slug=slugify(name))
    #         return Response(
    #             {"data": serializer.data, "success": "Campaign updated successfully."},
    #             status=status.HTTP_200_OK,
    #         )
    #     return Response(
    #         {"data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
    #     )
    
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
print(config.LIMIT_CAMPAIGN)

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
        if self.action in ["list", "retrieve"]:
            return TaskSerializer
        return TaskSerializer

    def perform_create(self, serializer):
        serializer.save()

    # @action(detail=True, methods=['post'], url_path="task/create")
    def create(self, request):
        # campaign = self.get_object()
        print("*"*100)
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
        object_set = UserTaskChecking.objects.filter(user=request.user, is_completed=False)
        if len(object_set) >= 1:
            return Response({"data": None, "message": "You already have a task started"}, status=status.HTTP_200_OK)
        serializers = UserTaskCheckingSerializer(data=request.data)
        if serializers.is_valid():
            task_obj = get_object_or_404(Task, pk=pk)
            serializers.save(user=request.user, task=task_obj, points_awarded=task_obj.points_reward)
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
            "content_usage"
        ]:
            obj_set = UserTaskChecking.objects.filter(user=request.user, is_completed=False)
            if len(obj_set) == 1:
                obj_set[0].end_date = now()
                obj_set[0].is_completed = True
                obj_set[0].save()

            return redirect(task_obj.external_link)
        else:
            return redirect(task_obj.external_link)
        return Response({"error": "Task type is not supported."}, status=status.HTTP_400_BAD_REQUEST)
