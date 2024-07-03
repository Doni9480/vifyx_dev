import json
from django.http import Http404
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from custom_tests.models import Test, Question, QuestionAnswer
from .serializers import (
    TestSerializer,
    TestDetailSerializer,
    TestEditSerializer,
    QuestionSerializer,
    TestVisibilitySerializer,
)
from django.db import transaction
from django.template.defaultfilters import slugify
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects.all()
    permission_classes = [IsAuthenticated]
    # parser_classes = [MultiPartParser]

    def get_queryset(self):
        pk = self.kwargs.get("pk")
        if self.action == "list":
            return Test.objects.all()
        elif self.action in ["retrieve", "partial_update", "update_visibility"]:
            return Test.objects.filter(pk=pk)
        elif self.action in ["question_list"]:
            test_objects = Test.objects.filter(pk=pk)
            if test_objects.count():
                return Question.objects.filter(test=test_objects[0])
            return []
        elif self.action in ["question_update", "question_destroy"]:
            return Question.objects.filter(pk=pk)
        else:
            return Test.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return TestSerializer
        elif self.action == "create":
            return TestEditSerializer
        elif self.action == "retrieve":
            return TestDetailSerializer
        elif self.action == "partial_update":
            return TestEditSerializer
        elif self.action == "update_visibility":
            return TestVisibilitySerializer
        elif self.action == "question_list":
            return QuestionSerializer
        elif self.action == "question_create":
            return QuestionSerializer
        elif self.action == "question_update":
            return QuestionSerializer
        elif self.action == "question_destroy":
            return QuestionSerializer
        return TestSerializer

    # @swagger_auto_schema(
    #     operation_description="Создание квеста\nВнимание!\nПри создании теста нужно использовать параметр [Сontent-type: multipart/form-data;]. Так как есть поле для изображения (preview)",
    #     request_body=TestEditSerializer,
    #     manual_parameters=[
    #         openapi.Parameter(
    #             'preview',
    #             openapi.IN_FORM,
    #             description="File to upload",
    #             type=openapi.TYPE_FILE
    #         )
    #     ],
    #     responses={201: openapi.Response("Успешное создание", TestEditSerializer())},
    # )
    # @transaction.atomic
    def create(self, request, *args, **kwargs):
        response_data = {}
        data = request.data
        data["slug"] = slugify(data["title"])
        data["user"] = request.user.pk
        data["language"] = str(request.user.language)
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            response_data["success"] = "ok."
            response_data["data"] = serializer.data
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            response_data["data"] = serializer.errors
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"data": serializer.data})

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"data": serializer.data})

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "success": "ok."})
        else:
            return Response(
                {"data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["patch"], url_path="<pk>/visibility")
    def update_visibility(self, request, pk=None):
        instance = self.get_object()
        if not instance:
            return Response(
                {"data": "Data not found!"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "success": "ok."})
        else:
            return Response(
                {"data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=["get"], url_path="<pk>/questions")
    def question_list(self, request, pk=None, *args, **kwargs):
        response_data = {}
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response_data["success"] = "ok."
        response_data["data"] = serializer.data
        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="question/create")
    @transaction.atomic
    def question_create(self, request, *args, **kwargs):
        response_data = {}
        test_obj = get_object_or_404(Test, pk=request.data.get("test"))
        request_data = dict(request.data)
        request_data["question"] = request_data["question"][0]
        request_data["test"] = test_obj.pk
        serializer = self.get_serializer(data=request_data)
        if serializer.is_valid():
            serializer.save()
            valid = True
            err = None
            if valid:
                response_data["success"] = "ok."
                response_data["data"] = serializer.data
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                response_data["data"] = err
        else:
            response_data["data"] = serializer.errors
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["patch"], url_path="question/<pk>/update")
    @transaction.atomic
    def question_update(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        if not request.user.id == instance.test.user.id:
            raise Http404()
        request_data = dict(request.data)
        request_data["question"] = request_data["question"][0]
        serializer = self.get_serializer(instance, data=request_data, partial=True)
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
        if not request.user.id == instance.test.user.id:
            raise Http404()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
