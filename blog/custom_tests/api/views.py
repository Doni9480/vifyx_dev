import json
from django.http import Http404
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from custom_tests.models import (
    Test, 
    Question, 
    QuestionAnswer, 
    TestView, 
    Category, 
    Subcategory,
    TestDayView,
    TestWeekView,
    TestLike,
)
from users.utils import opening_access
from .serializers import (
    TestSerializer,
    TestDetailSerializer,
    TestEditSerializer,
    QuestionSerializer,
    TestVisibilitySerializer,
    SubcategorySerializer,
)
from django.db import transaction
from blog.utils import get_request_data
from blogs.models import Blog
from django.template.defaultfilters import slugify as default_slugify
from transliterate import slugify
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from blog.utils import set_language_to_user, MyPagination
from blogs.utils import get_filter_kwargs, get_obj_set, get_category
from custom_tests.api.utils import get_more_to_tests
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from operator import attrgetter


class TestViewSet(viewsets.ModelViewSet):
    queryset = Test.objects_show.all()
    permission_classes = [IsAuthenticated]
    permission_classes_by_action = dict.fromkeys(['list', 'retrieve', 'add_view'], [AllowAny])
    pagination_class = MyPagination
    # parser_classes = [MultiPartParser]

    def get_queryset(self):
        pk = self.kwargs.get("pk")
        if self.action == "list":
            return Test.level_access_objects.all()
        elif self.action in ["partial_update", "update_visibility"]:
            return Test.objects_show.filter(pk=pk)
        elif self.action == 'get_subcategory':
            return Category.objects.all()
        elif self.action in ["retrieve"]:
            return Test.objects.filter(pk=pk)
        elif self.action in ["question_list"]:
            test_objects = Test.objects.filter(pk=pk)
            if test_objects.count():
                opening_access(test_objects.first(), self.request.user)
                return Question.objects.filter(test=test_objects.first())
            return []
        elif self.action in ["question_update", "question_destroy"]:
            return Question.objects.filter(pk=pk)
        else:
            return Test.objects_show.all()

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
    
    def get_permissions(self):
        try:
            # return permission_classes depending on `action`
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            # action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]

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
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        _ = get_object_or_404(Blog, user=request.user.id, id=request.data.get('blog'))
        
        response_data = {}
        
        if request.user.is_authenticated and request.user.is_published_post:
            data = request.data.dict()
            data["user"] = request.user.pk
            serializer = self.get_serializer(data=data, user=request.user)
            if serializer.is_valid():
                test = serializer.save()
                test.user = request.user
                test.save()
                response_data["success"] = "ok."
                response_data["data"] = serializer.data
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                response_data["data"] = serializer.errors
        else:
            response_data['ban'] = 'You can\'t publish tests.'
            
        print(response_data)
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        request = set_language_to_user(request)
        filter_kwargs, subcategories, select_subcategories = get_category(get_filter_kwargs(request), request, 'tests')
        obj_set = get_obj_set(Test.level_access_objects.filter(**filter_kwargs), request.user)
        obj_set = sorted(obj_set, key=attrgetter('date'), reverse=True)
        
        tests = TestSerializer(
            obj_set,
            many=True,
        ).data
        tests = get_more_to_tests(tests)
        page = self.paginate_queryset(tests)
        return self.get_paginated_response(page)
    
    def retrieve(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        opening_access(instance, request.user, is_show=True)
        serializer_data = self.get_serializer(instance).data
        if instance.is_not_subscribed:
            serializer_data['is_not_subscribed'] = True            
        return Response({"data": serializer_data})

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        _data = get_request_data(request.data)
        if _data.get('language', False):
            del _data['language']
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=_data, partial=True)
        if serializer.is_valid():
            test = serializer.save()
            return Response({"slug": test.slug, "success": "ok."})
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
        if not request.user.id == instance.test.user.id:
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
        instance = get_object_or_404(Question, id=pk)
        if not request.user.id == instance.test.user.id:
            raise Http404()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["patch"], url_path="<pk>/hide_test")
    def hide_test(self, request, pk=None):
        data = {}

        test = self.get_object()
        if request.user == test.user:
            test.hide_to_user = True
        elif request.user.is_staff:
            test.hide_to_moderator = True
        else:
            raise Http404()

        test.save()

        data["success"] = "ok."

        return Response(data)

    @action(detail=True, methods=["patch"], url_path="<pk>/show_test")
    def show_test(self, request, pk=None):
        data = {}

        test = self.get_object()

        if request.user != test.user and not request.user.is_staff:
            raise Http404()

        if request.user == test.user and not test.hide_to_moderator:
            test.hide_to_user = False
        elif request.user.is_staff:
            test.hide_to_moderator = False
        else:
            data["ban"] = "You can't show the test"

        test.save()

        if not data.get("ban", False):
            data["success"] = "ok."

        return Response(data)
        
    @action(detail=True, methods=["post"], url_path="views/add/<pk>")
    @transaction.atomic
    def add_view(self, request, pk=None):
        if request.user.is_authenticated:
            test = self.get_object()
            opening_access(test, request.user)
            views = [TestView, TestWeekView, TestDayView]
            for view in views:
                if not view.objects.filter(test=test).filter(user=request.user.id).first():
                    view.objects.create(test=test, user=request.user)
        return Response({"success": "ok."})
    
    @action(detail=True, methods=["post"], url_path="<pk>/get_subcategory")
    def get_subcategory(self, request, pk=None):
        category = self.get_object()
        subcategories_set = Subcategory.objects.filter(category=category)
        subcategories = SubcategorySerializer(
            subcategories_set, many=True
        ).data
        return Response({"subcategories": subcategories})
    
    @action(detail=True, methods=["post"], url_path="<pk>/send_like")
    def send_like(self, request, pk=None):
        instance = self.get_object()
        opening_access(instance, request.user)
        if instance.user == request.user:
            raise Http404()
        
        data = {}
        
        test_filter = TestLike.objects.filter(test=instance, user=request.user)
        if not test_filter:
            data['add'] = True
            TestLike.objects.create(test=instance, user=request.user)
        else:
            data['add'] = False
            test_filter.first().delete()
        
        data["success"] = "ok."
        
        return Response(data)