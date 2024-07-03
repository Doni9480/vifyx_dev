import json
from django.http import Http404
from rest_framework import viewsets, status
from rest_framework.decorators import action, parser_classes
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify
from django.db import transaction

from quests.models import Quest, QuestionQuest, QuestionQuestAnswer
from .serializers import (
    QuestSerializer,
    QuestVisibilitySerializer,
    QuestDetailSerializer,
    QuestionQuestSerializer,
    QuestionQuestDetailSerializer,
    QuestionQuestAnswerSerializer,
)
from blog.decorators import recaptcha_checking


class QuestViewSet(viewsets.ModelViewSet):
    queryset = Quest.objects.all()
    serializer_class = QuestSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_description="Создание квеста\nВнимание!\nПри создании теста нужно использовать параметр [Сontent-type: multipart/form-data;]. Так как есть поле для изображения (preview)",
        request_body=QuestSerializer,
        manual_parameters=[
            openapi.Parameter(
                'preview',
                openapi.IN_FORM,
                description="File to upload",
                type=openapi.TYPE_FILE
            )
        ],
        responses={201: openapi.Response("Успешное создание", QuestSerializer())},
    )
    @transaction.atomic
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

    @swagger_auto_schema(
        operation_description="Получение детализаций квеста",
        responses={
            200: openapi.Response("Успешное получение", QuestDetailSerializer())
        },
    )
    def retrieve(self, request, *args, **kwargs):
        response_data = {}
        instance = self.get_object()
        serializer = QuestDetailSerializer(instance)
        response_data["data"] = serializer.data
        return Response(response_data)

    @swagger_auto_schema(
        operation_description="Изменение детализаций квеста",
        request_body=QuestDetailSerializer,
        responses={
            200: openapi.Response("Успешное изменение", QuestDetailSerializer())
        },
    )
    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        response_data = {}
        instance = self.get_object()
        serializer = QuestDetailSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            response_data["data"] = serializer.data
            response_data["success"] = "ok."
            return Response(response_data)
        else:
            response_data["data"] = serializer.errors
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Удаление квеста",
        responses={204: openapi.Response("Успешное удаление")},
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        operation_description="Управление видимости квеста",
        request_body=QuestVisibilitySerializer,
        responses={
            200: openapi.Response("Успешное создание", QuestVisibilitySerializer())
        },
    )
    @action(detail=True, methods=["patch"], url_path="<pk>/visibility", permission_classes=[IsAuthenticated])
    @transaction.atomic
    def visibility(self, request, pk=None):
        data = {}
        quest = self.get_object()
        serializer = QuestVisibilitySerializer(
            instance=quest, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            data["data"] = serializer.data
            data["success"] = "ok."
            return Response(data, status=status.HTTP_200_OK)
        else:
            data["data"] = serializer.errors
            return Response(data, status=status.HTTP_400_BAD_REQUEST)


class QuestionQuestViewSet(viewsets.ModelViewSet):
    queryset = QuestionQuest.objects.all()
    serializer_class = QuestionQuestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return QuestionQuest.objects.filter(quest_id=self.kwargs["quest_pk"])

    @swagger_auto_schema(
        operation_description="Создание вопросов для квеста",
        request_body=QuestionQuestDetailSerializer,
        responses={
            201: openapi.Response("Успешное создание", QuestionQuestDetailSerializer())
        },
    )
    @transaction.atomic
    def create(self, request, quest_pk=None):
        response_data = {}
        quest_obj = get_object_or_404(Quest, pk=quest_pk)
        request_data = dict(request.data)
        request_data["quest"] = quest_obj.pk
        serializer = QuestionQuestDetailSerializer(data=request_data)
        if serializer.is_valid():
            serializer.save()
            response_data["success"] = "ok."
            response_data["data"] = serializer.data
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            response_data["data"] = serializer.errors
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Изменение вопросов квеста",
        request_body=QuestionQuestSerializer,
        responses={
            200: openapi.Response("Успешное изменение", QuestionQuestSerializer())
        },
    )
    @transaction.atomic
    def partial_update(self, request, quest_pk=None, pk=None):
        response_data = {}
        question_obj = get_object_or_404(QuestionQuest, pk=pk)
        if not request.user.id == question_obj.quest.user.id:
            raise Http404()

        request_data = dict(request.data)
        request_data["question"] = request_data["question"][0]
        request_data["answers_set"] = json.loads(request_data["answers_set"][0])
        request_data["g_recaptcha_response"] = request_data["g_recaptcha_response"][0]
        serializer = QuestionQuestSerializer(
            question_obj, data=request_data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            valid = True
            err = None
            for item in request_data["answers_set"]:
                answer_obj = QuestionQuestAnswer.objects.get(id=item.get("id"))
                answer = QuestionQuestAnswerSerializer(
                    answer_obj, data=item, partial=True
                )
                if not answer.is_valid():
                    err = answer.errors
                else:
                    answer.save()
            if valid:
                response_data["data"] = serializer.data
                response_data["success"] = "ok."
                return Response(response_data)
            else:
                response_data["data"] = err
        else:
            response_data["data"] = serializer.errors
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Удаление вопроса квеста по id",
        responses={204: openapi.Response("Успешное удаление")},
    )
    @transaction.atomic
    def destroy(self, request, quest_pk=None, pk=None):
        question_obj = get_object_or_404(QuestionQuest, pk=pk)
        if not request.user.id == question_obj.quest.user.id:
            raise Http404()
        question_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# from rest_framework.views import APIView
# from rest_framework import generics
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.parsers import MultiPartParser, FormParser
# from rest_framework.response import Response
# from rest_framework import status
# from drf_yasg.utils import swagger_auto_schema
# from django.shortcuts import get_object_or_404
# from django.db import transaction
# from django.template.defaultfilters import slugify
# from rest_framework.viewsets import ModelViewSet
# from drf_yasg.utils import swagger_auto_schema
# from drf_yasg import openapi

# from quests.models import Quest, QuestionQuest, QuestionQuestAnswer
# from .serializers import (
#     QuestSerializer,
#     QuestVisibilitySerializer,
#     QuestDetailSerializer,
#     QuestionQuestSerializer,
#     QuestionQuestDetailSerializer,
# )

# class CreateQuestView(ModelViewSet):
#     permission_classes = [IsAuthenticated]
#     parser_classes = [MultiPartParser, FormParser]

#     @swagger_auto_schema(
#         operation_description="Создание квеста\nВнимание!\nПри создании теста нужно использовать параметр [Сontent-type: multipart/form-data;]. Так как есть поле для изображения (preview)",
#         request_body=QuestSerializer,
#         responses={201: openapi.Response("Успешное создание", QuestSerializer())},
#     )
#     @transaction.atomic
#     def post(self, request):
#         data = request.data.copy()
#         data["slug"] = slugify(data["title"])
#         data["user"] = request.user.pk
#         data["language"] = str(request.user.language)
#         serializer = QuestSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"success": "ok.", "data": serializer.data}, status=status.HTTP_201_CREATED)
#         return Response({"data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

# class QuestsListView(ModelViewSet):
#     queryset = Quest.objects.all()
#     serializer_class = QuestSerializer

#     @swagger_auto_schema(
#         operation_description="Получение списка квестов",
#         responses={200: openapi.Response("Успешное создание", QuestSerializer(many=True))},
#     )
#     def get(self, request, *args, **kwargs):
#         return super().get(request, *args, **kwargs)

# class QuestDetailView(ModelViewSet):

#     @swagger_auto_schema(
#         operation_description="Получение детализаций квеста",
#         responses={200: openapi.Response("Успешное получение", QuestDetailSerializer())},
#     )
#     def get(self, request, pk):
#         quest = get_object_or_404(Quest, pk=pk)
#         serializer = QuestDetailSerializer(quest)
#         return Response({"data": serializer.data})

# class QuestEditView(ModelViewSet):
#     permission_classes = [IsAuthenticated]

#     @swagger_auto_schema(
#         operation_description="Изменение детализаций квеста",
#         request_body=QuestDetailSerializer,
#         responses={200: openapi.Response("Успешное изменение", QuestDetailSerializer())},
#     )
#     def patch(self, request, pk):
#         quest = get_object_or_404(Quest, pk=pk)
#         serializer = QuestDetailSerializer(quest, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"success": "ok.", "data": serializer.data})
#         return Response({"data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

# class QuestDeleteView(ModelViewSet):
#     permission_classes = [IsAuthenticated]

#     @swagger_auto_schema(
#         operation_description="Удаление квеста",
#         responses={204: openapi.Response("Успешное удаление", QuestDetailSerializer())},
#     )
#     def delete(self, request, pk):
#         quest = get_object_or_404(Quest, pk=pk)
#         quest.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

# class QuestVisibilityView(ModelViewSet):
#     permission_classes = [IsAuthenticated]

#     @swagger_auto_schema(
#         operation_description="Управление видимости квеста",
#         request_body=QuestVisibilitySerializer,
#         responses={200: openapi.Response("Успешное создание", QuestVisibilitySerializer())},
#     )
#     @transaction.atomic
#     def patch(self, request, pk):
#         quest = get_object_or_404(Quest, pk=pk)
#         serializer = QuestVisibilitySerializer(quest, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"success": "ok.", "data": serializer.data})
#         return Response({"data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

# class QuestQuestionCreateView(ModelViewSet):
#     permission_classes = [IsAuthenticated]

#     @swagger_auto_schema(
#         operation_description="Создание вопросов для квеста",
#         request_body=QuestionQuestDetailSerializer,
#         responses={200: openapi.Response("Успешное создание", QuestionQuestDetailSerializer())},
#     )
#     @transaction.atomic
#     def post(self, request, pk):
#         quest = get_object_or_404(Quest, pk=pk)
#         data = request.data.copy()
#         data["quest"] = quest.pk
#         serializer = QuestionQuestDetailSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"success": "ok.", "data": serializer.data}, status=status.HTTP_201_CREATED)
#         return Response({"data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

# class QuestQuestionEditView(ModelViewSet):
#     permission_classes = [IsAuthenticated]

#     @swagger_auto_schema(
#         operation_description="Изменение вопросов квеста",
#         request_body=QuestionQuestSerializer,
#         responses={200: openapi.Response("Успешное изменение", QuestionQuestSerializer())},
#     )
#     @transaction.atomic
#     def patch(self, request, pk):
#         question = get_object_or_404(QuestionQuest, pk=pk)
#         if request.user.id != question.quest.user.id:
#             raise Http404()
#         data = request.data.copy()
#         data["question"] = data.get("question")[0]
#         data["answers_set"] = json.loads(data.get("answers_set")[0])
#         data["g_recaptcha_response"] = data.get("g_recaptcha_response")[0]
#         serializer = QuestionQuestSerializer(question, data=data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             for item in data["answers_set"]:
#                 answer = get_object_or_404(QuestionQuestAnswer, id=item.get("id"))
#                 answer_serializer = QuestionQuestAnswerSerializer(answer, data=item, partial=True)
#                 if answer_serializer.is_valid():
#                     answer_serializer.save()
#             return Response({"success": "ok.", "data": serializer.data})
#         return Response({"data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

# class QuestQuestionDeleteView(ModelViewSet):
#     permission_classes = [IsAuthenticated]

#     @swagger_auto_schema(
#         operation_description="Удаление вопроса квеста по id",
#         responses={204: openapi.Response("Успешное удаление", QuestionQuestSerializer())},
#     )
#     @transaction.atomic
#     def delete(self, request, pk):
#         question = get_object_or_404(QuestionQuest, pk=pk)
#         if request.user.id != question.quest.user.id:
#             raise Http404()
#         question.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
