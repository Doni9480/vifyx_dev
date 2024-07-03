from rest_framework import viewsets, status, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.http import Http404


from surveys.api.serializers import *
from surveys.models import SurveyTag, SurveyView, SurveyVote, Survey, DraftSurvey
from surveys.api.utils import get_views_and_comments_to_surveys
from surveys.utils import opening_access
from users.models import User, Percent
from blog.decorators import recaptcha_checking
from blogs.models import Blog
from comments.models import Comment


class SurveyViewSet(viewsets.ModelViewSet):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        if self.action in ["add_view", "hide_survey", "show_survey"]:
            return SurveyNoneSerializer
        elif self.action == "send_scores_to_option":
            return SurveyScoresSerializer
        else:
            return SurveySerializer

    def create(self, request, *args, **kwargs):
        _ = get_object_or_404(Blog, user=request.user.id, id=request.data["blog"])

        data = {}

        if request.user.is_authenticated and request.user.is_published_post:
            request.data._mutable = True
            request.data["language"] = request.user.language

            draft = DraftSurvey.objects.filter(
                user=request.user.id, blog=request.data["blog"]
            )
            if not request.data.get("preview", False):
                if draft and draft[0].preview:
                    request.data["preview"] = draft[0].preview

            request.data._mutable = False

            serializer = SurveySerializer(data=request.data, user=request.user.id)

            if serializer.is_valid():
                survey = serializer.save()

                survey.user = request.user
                survey.save()
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
        if not request.user.is_staff:
            surveys = SurveyIndexSerializer(
                Survey.level_access_objects.filter(
                    hide_to_user=False,
                    hide_to_moderator=False,
                    language=request.user.language,
                ),
                many=True,
            ).data
        else:
            surveys = SurveyIndexSerializer(
                Survey.level_access_objects.filter(language=request.user.language),
                many=True,
            ).data

        surveys = get_views_and_comments_to_surveys(surveys)

        return Response({"data": surveys})

    def retrieve(self, request, pk=None):
        survey_model = get_object_or_404(Survey.objects, id=pk)
        if opening_access(survey_model, request.user):
            raise Http404()

        survey = SurveyShowSerializer(survey_model).data

        if survey["language"] == "2":
            survey["language"] = "Russian"
        else:
            survey["language"] = "English"

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

        survey["user"] = User.objects.get(id=survey["user"]).username

        return Response({"data": survey})

    def partial_update(self, request, pk=None):
        data = {}

        instance = get_object_or_404(Survey.objects, id=pk, user=request.user.id)

        # language a not edit
        request.data._mutable = True
        if request.data.get("language", False):
            del request.data["language"]
        request.data._mutable = False

        serializer = SurveySerializer(
            instance=instance, data=request.data, partial=True, user=request.user.id
        )

        if serializer.is_valid():
            survey = serializer.save()

            data["success"] = "Successful updated a survey."
            data["slug"] = survey.slug
        else:
            data = serializer.errors

        return Response(data)

    def destroy(self, request, pk=None):
        try:
            instance = get_object_or_404(Survey, id=pk)
            if instance.user != request.user:
                raise Exception()
        except Exception:
            raise Http404()

        if request.method == "DELETE":
            data = {}

            tags = SurveyTag.objects.filter(survey=instance)
            for tag in tags:
                tag.delete()

            answers = SurveyRadio.objects.filter(survey=instance)
            print(answers)
            for answer in answers:
                answer.delete()

            instance.delete()

            data["success"] = "Successful deleted a survey."

            return Response(data)

    @action(detail=True, methods=["post"], url_path="<pk>/add_view")
    def add_view(self, request, pk=None):
        if request.user.is_authenticated:
            survey = get_object_or_404(Survey.objects, id=pk)
            if opening_access(survey, request.user):
                raise Http404()
            view = SurveyView.objects.filter(survey=survey).filter(user=request.user.id)
            if not view:
                SurveyView.objects.create(survey=survey, user=request.user)

        return Response({"success": "ok."})

    @action(detail=True, methods=["post"], url_path="send_scores_to_option/<int:pk>")
    def send_scores_to_option(self, request, pk=None):
        data = {}

        option = get_object_or_404(SurveyRadio, id=pk)
        if opening_access(option.survey, request.user):
            raise Http404()

        if (
            (SurveyVote.objects.filter(user=request.user.id, survey=option.survey))
            or int(option.survey.language) != int(request.user.language)
            or (
                (option.survey.hide_to_moderator or option.survey.hide_to_user)
                and not (option.survey.user == request.user or request.user.is_staff)
            )
        ):
            raise Http404()

        serializer = SurveyScoresSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user

            scores = int(serializer.validated_data["scores"])
            user.scores -= scores
            if user.scores <= 0:
                data["error_scores"] = "you have fewer scores than you indicated."
            elif scores <= 0:
                data["error_scores"] = "you cannot enter a negative value."
            else:
                user.save()

                admin = User.objects.filter(is_superuser=True)[0]
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

        survey = get_object_or_404(Survey.objects, id=pk)
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

        survey = get_object_or_404(Survey.objects, id=pk)

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


class DraftSurveyViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    
    def get_serializer_class(self):
        return DraftSurveySerializer

    def create(self, request):
        data = {}

        instance = DraftSurvey.objects.filter(
            user=request.user.id, blog=request.data["blog"]
        )
        if not instance:
            serializer = DraftSurveySerializer(data=request.data)

            if serializer.is_valid():
                draft_survey = serializer.save()

                draft_survey.user = request.user
                draft_survey.save()
            else:
                data = serializer.errors
        else:
            instance = instance[0]
            serializer = DraftSurveySerializer(
                instance, data=request.data, partial=True
            )

            if serializer.is_valid():
                draft_survey = serializer.save()
            else:
                data = serializer.errors

        if not data:
            data["success"] = "ok."
        print(data)

        return Response(data)
