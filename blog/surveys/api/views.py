from rest_framework import viewsets, status, mixins
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser

from django.db import transaction
from django.http import Http404, QueryDict


from surveys.api.serializers import *
from surveys.models import (
    SurveyTag, 
    SurveyView, 
    SurveyVote, 
    Survey, 
    DraftSurvey, 
    Category, 
    Subcategory,
    SurveyDayView,
    SurveyWeekView
)
from surveys.api.utils import get_views_and_comments_to_surveys
from users.utils import opening_access
from users.models import User, Percent
from blog.decorators import recaptcha_checking
from blog.utils import custom_get_object_or_404 as get_object_or_404, get_request_data, set_language_to_user, MyPagination
from blogs.models import Blog
from blogs.utils import get_filter_kwargs, get_obj_set, get_category

from operator import attrgetter


class SurveyViewSet(viewsets.ModelViewSet):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = [IsAuthenticated]
    permission_classes_by_action = dict.fromkeys(['list', 'retrieve'], [AllowAny])
    pagination_class = MyPagination
    # parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        if self.action in ["add_view", "hide_survey", "show_survey"]:
            return SurveyNoneSerializer
        elif self.action == "send_scores_to_option":
            return SurveyScoresSerializer
        else:
            return SurveySerializer
        
    def get_queryset(self):
        if self.action == 'send_scores_to_option':
            return SurveyRadio.objects.all()
        if self.action == 'get_subcategory':
            return Category.objects.all()
        return super().get_queryset()
    
    def get_permissions(self):
        try:
            # return permission_classes depending on `action`
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            # action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]
    
    def custom_get_object(self, **params):
        queryset = self.filter_queryset(self.get_queryset())

        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs, **params)

        self.check_object_permissions(self.request, obj)

        return obj

    def create(self, request, *args, **kwargs):
        _ = get_object_or_404(Blog, user=request.user.id, id=request.data.get("blog"))

        data = {}

        if request.user.is_authenticated and request.user.is_published_post:
            _data = get_request_data(request.data)
            
            draft = DraftSurvey.objects.filter(
                user=request.user.id, blog=_data["blog"]
            )
            if not _data.get("preview", False):
                if draft and draft[0].preview:
                    _data["preview"] = draft[0].preview

            serializer = SurveySerializer(data=_data, user=request.user)

            if serializer.is_valid():
                survey = serializer.save()
                
                if draft:
                    draft[0].delete()

                data["success"] = "Successful created a new survey."
                data["slug"] = survey.slug
            else:
                data = serializer.errors
        else:
            data["ban"] = "You can't publish surveys."
            
        return Response(data)

    def list(self, request, *args, **kwargs):
        request = set_language_to_user(request)
        filter_kwargs, subcategories, select_subcategories = get_category(get_filter_kwargs(request), request, 'quests')
        obj_set = get_obj_set(Survey.level_access_objects.filter(**filter_kwargs), request.user)
        obj_set = sorted(obj_set, key=attrgetter('date'), reverse=True)
            
        surveys = SurveyIndexSerializer(
            obj_set,
            many=True,
        ).data

        surveys = get_views_and_comments_to_surveys(surveys)
        page = self.paginate_queryset(surveys)
        return self.get_paginated_response(page) 

    def retrieve(self, request, pk=None):
        survey_model = self.get_object()
        request = set_language_to_user(request)
        opening_access(survey_model, request.user, is_show=True)
        survey = SurveyShowSerializer(survey_model).data

        tags = SurveyTag.objects.filter(survey_id=survey["id"])
        survey["tags"] = []
        for tag in tags:
            survey["tags"].append(tag.title)

        options = SurveyRadio.objects.filter(survey_id=survey["id"])
        survey["options"] = []
        for option in options:
            vote = False
            votes_user = SurveyVote.objects.filter(user=request.user.id)

            vote_model = votes_user.filter(option=option, survey=survey["id"])
            if vote_model:
                vote = True

            survey["options"].append(
                {"option": option.title, "scores": option.scores, "is_vote": vote}
            )
            
        if survey_model.is_not_subscribed:
            del survey['options']
            del survey['tags']
            survey['is_not_subscribed'] = True

        survey["user"] = User.objects.get(id=survey["user"]).username

        return Response({"data": survey})

    def partial_update(self, request, pk=None):
        data = {}

        instance = self.custom_get_object(user=request.user)
        
        _data = get_request_data(request.data)

        # language a not edit
        if _data.get('language', False):
            del _data['language']

        serializer = SurveySerializer(
            instance=instance, data=_data, partial=True, user=request.user
        )

        if serializer.is_valid():
            survey = serializer.save()

            data["success"] = "Successful updated a survey."
            data["slug"] = survey.slug
        else:
            data = serializer.errors

        return Response(data)

    def destroy(self, request, pk=None):
        instance = self.get_object()
        if instance.user != request.user:
            raise Http404()

        if request.method == "DELETE":
            data = {}

            tags = SurveyTag.objects.filter(survey=instance)
            for tag in tags:
                tag.delete()

            answers = SurveyRadio.objects.filter(survey=instance)
            for answer in answers:
                answer.delete()

            instance.delete()

            data["success"] = "Successful deleted a survey."

            return Response(data)

    @action(detail=True, methods=["post"], url_path="<pk>/view/add")
    def add_view(self, request, pk=None):
        survey = self.get_object()
        opening_access(survey, request.user)
        views = [SurveyView, SurveyDayView, SurveyWeekView]
        for view in views:
            if not view.objects.filter(survey=survey).filter(user=request.user.id).first():
                view.objects.create(survey=survey, user=request.user)
        return Response({"success": "ok."})

    @action(detail=True, methods=["post"], url_path="send_scores_to_option/<pk>")
    def send_scores_to_option(self, request, pk=None):
        data = {}

        option = self.get_object()
        opening_access(option.survey, request.user)

        if (
            (SurveyVote.objects.filter(user=request.user.id, survey=option.survey))
            or (option.survey.hide_to_moderator or option.survey.hide_to_user and not request.user.is_staff)
        ):
            raise Http404()

        serializer = SurveyScoresSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            admin  = User.objects.filter(is_superuser=True).first()
            if user == admin:
                user = admin

            scores = int(serializer.validated_data["scores"])

            if user.scores <= scores:
                data["error_scores"] = "you have fewer scores than you indicated."
            elif scores <= 0:
                data["error_scores"] = "you cannot enter a negative value."
            else:
                user.scores -= scores
                user.save()
                
                percent = Percent.objects.all()[0].percent / 100
                admin.scores += int(scores * percent) or 1
                admin.save()

                reverse_percent = 1 - Percent.objects.all()[0].percent / 100
                scores = int(scores * reverse_percent) or 1

                option.scores += scores
                option.save()

                # user is vote
                SurveyVote.objects.create(user=user, survey=option.survey, option=option)

                data["success"] = "ok."
                data["scores"] = option.scores
        else:
            data = serializer.errors

        return Response(data)

    @action(detail=True, methods=["patch"], url_path="<pk>/hide_survey")
    def hide_survey(self, request, pk=None):
        data = {}

        survey = self.get_object()
        if request.user == survey.user:
            survey.hide_to_user = True
        elif request.user.is_staff:
            survey.hide_to_moderator = True
        else:
            raise Http404()

        survey.save()

        data["success"] = "ok."

        return Response(data)

    @action(detail=True, methods=["patch"], url_path="<pk>/show_survey")
    def show_survey(self, request, pk=None):
        data = {}

        survey = self.get_object()

        if request.user != survey.user and not request.user.is_staff:
            raise Http404()

        if request.user == survey.user and not survey.hide_to_moderator:
            survey.hide_to_user = False
        elif request.user.is_staff:
            survey.hide_to_moderator = False
        else:
            data["ban"] = "You can't show the survey"

        survey.save()

        if not data.get("ban", False):
            data["success"] = "ok."

        return Response(data)
    
    @action(detail=True, methods=["post"], url_path="<pk>/get_subcategory")
    def get_subcategory(self, request, pk=None):
        category = self.get_object()
        subcategories_set = Subcategory.objects.filter(category=category)
        subcategories = SubcategorySerializer(
            subcategories_set, many=True
        ).data
        return Response({"subcategories": subcategories})


class DraftSurveyViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        return DraftSurveySerializer

    def create(self, request):
        data = {}
        
        _data = get_request_data(request.data)
        try:
            instance = get_object_or_404(
                DraftSurvey,
                user=request.user.id, 
                blog=request.data["blog"]
            )
            serializer = DraftSurveySerializer(
                instance, data=_data, partial=True, user=request.user
            )
        except Http404 as e:
            serializer = DraftSurveySerializer(data=_data, user=request.user)
            
        if serializer.is_valid():
            serializer.save()
        else:
            data = serializer.errors
                
        if not data:
            data["success"] = "ok."

        return Response(data)
