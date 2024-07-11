from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_list_or_404, get_object_or_404
from django.http import Http404
from django.db import transaction

from comments.api.serializers import *
from comments.models import Comment, Answer
from comments.api.utils import (
    func_is_valid_comment,
    func_is_valid_answer,
    opening_access,
)

from posts.models import Post
from surveys.models import Survey
from custom_tests.models import Test
from quests.models import Quest
from users.models import User
from blog.utils import set_language_to_user


class CommentViewSet(viewsets.GenericViewSet):
    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticated, IsAuthenticatedOrReadOnly]
    permission_classes_by_action = dict.fromkeys([
        'index_comment_post',
        'show_comment_post',
        'index_comment_survey',
        'show_comment_survey',
        'show_answer_quest',
        'show_answer_test',
        'show_answer_post',
        'show_answer_survey',
        'index_answer_post',
        'index_answer_survey',
        'index_answer_test',
        'index_answer_quest'
    ], [AllowAny])

    def get_serializer_class(self):
        if self.action == "create_comment_to_post":
            return CommentPostSerializer
        elif self.action == "create_comment_to_survey":
            return CommentSurveySerializer
        elif self.action == "create_comment_to_test":
            return CommentTestSerializer
        elif self.action == "create_comment_to_quest":
            return CommentQuestSerializer
        elif self.action in ["index_comment_post", "show_comment_post"]:
            return CommentPostShowSerializer
        elif self.action in ["index_comment_survey", "show_comment_survey"]:
            return CommentSurveyShowSerializer
        elif self.action in ["index_comment_test", "show_comment_test"]:
            return CommentTestShowSerializer
        elif self.action in ["index_comment_quest", "show_comment_quest"]:
            return CommentQuestShowSerializer
        return CommentFullSerializer
    
    def get_permissions(self):
        try:
            # return permission_classes depending on `action`
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            # action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]

    @action(detail=True, methods=["post"], url_path="create/post")
    @transaction.atomic
    def create_comment_to_post(self, request):
        serializer = CommentPostSerializer(data=request.data)
        data = func_is_valid_comment(request, serializer)

        post = Post.objects.get(id=request.data.get("post"))
        if opening_access(post, request.user):
            raise Http404()

        return Response(data)

    @action(detail=False, methods=["get"], url_path="index/post/<pk>")
    def index_comment_post(self, request, pk):
        post = get_object_or_404(Post, id=pk)
        request = set_language_to_user(request)
        if opening_access(post, request.user):
            raise Http404()

        comments = get_list_or_404(Comment, post=post)
        comments = CommentPostShowSerializer(comments, many=True).data

        for comment in comments:
            comment["user"] = User.objects.get(id=comment["user"]).username

            if comment["delete_from_user"]:
                comment["text"] = "This comment was deleted by the user."

        return Response({"data": comments})

    @action(detail=True, methods=["get"], url_path="show/post/<pk>")
    def show_comment_post(self, request, pk):
        comment = get_object_or_404(Comment, id=pk)
        post = get_object_or_404(Post, id=comment.post.pk)

        request = set_language_to_user(request)
        if opening_access(post, request.user):
            raise Http404()

        comment = CommentPostShowSerializer(comment).data

        if comment["delete_from_user"]:
            comment["text"] = "This comment was deleted by the user."

        comment["user"] = User.objects.get(id=comment["user"]).username

        return Response({"data": comment})

    @action(detail=True, methods=["post"], url_path="create/survey")
    @transaction.atomic
    def create_comment_to_survey(self, request):
        serializer = CommentSurveySerializer(data=request.data)
        data = func_is_valid_comment(request, serializer)

        survey = Survey.objects.get(id=request.data.get("survey"))
        if opening_access(survey, request.user):
            raise Http404()

        return Response(data)

    @action(detail=False, methods=["get"], url_path="index/survey/<pk>")
    def index_comment_survey(self, request, pk):
        survey = get_object_or_404(Survey, id=pk)
        request = set_language_to_user(request)
        if opening_access(survey, request.user):
            raise Http404()

        comments = get_list_or_404(Comment, survey=survey)
        comments = CommentSurveyShowSerializer(comments, many=True).data

        for comment in comments:
            comment["user"] = User.objects.get(id=comment["user"]).username

            if comment["delete_from_user"]:
                comment["text"] = "This comment was deleted by the user."

        return Response({"data": comments})

    @action(detail=True, methods=["get"], url_path="show/survey/<pk>")
    def show_comment_survey(self, request, pk):
        comment = get_object_or_404(Comment, id=pk)
        survey = get_object_or_404(Survey, id=comment.survey.pk)


        request = set_language_to_user(request)
        if opening_access(survey, request.user):
            raise Http404()

        comment = CommentSurveyShowSerializer(comment).data
        if comment["delete_from_user"]:
            comment["text"] = "This comment was deleted by the user."

        comment["user"] = User.objects.get(id=comment["user"]).username

        return Response({"data": comment})

    @action(detail=True, methods=["post"], url_path="create/test")
    @transaction.atomic
    def create_comment_to_test(self, request, *args, **kwargs):
        serializer = CommentTestSerializer(data=request.data)
        data = func_is_valid_comment(request, serializer)
        return Response(data)

    @action(detail=False, methods=["get"], url_path="index/test/<pk>")
    def index_comment_test(self, request, pk):
        request = set_language_to_user(request)
        try:
            # if not request.user.is_staff:
            #     if not Test.objects.filter(
            #         id=pk,
            #         hide_to_user=False,
            #         hide_to_moderator=False,
            #         language=request.user.language,
            #     ):
            #         raise Exception()

            comments = Comment.objects.filter(test=pk)
            if not comments:
                raise Exception()

            comments = CommentTestShowSerializer(comments, many=True).data

            for comment in comments:
                comment["user"] = User.objects.get(id=comment["user"]).username

                if comment["delete_from_user"]:
                    comment["text"] = "This comment was deleted by the user."
        except Exception:
            raise Http404()

        return Response({"data": comments})

    @action(detail=True, methods=["get"], url_path="show/test/<pk>")
    def show_comment_test(self, request, pk):
        request = set_language_to_user(request)
        try:
            comment = get_object_or_404(Comment, id=pk)
            if not request.user.is_staff:
                if not Test.objects.filter(
                    id=comment.post,
                    hide_to_user=False,
                    hide_to_moderator=False,
                    language=request.user.language,
                ):
                    raise Exception()

            comment = CommentTestShowSerializer(comment).data

            if comment["delete_from_user"]:
                comment["text"] = "This comment was deleted by the user."

            comment["user"] = User.objects.get(id=comment["user"]).username

        except Exception:
            raise Http404()

        return Response({"data": comment})

    @action(detail=True, methods=["post"], url_path="create/quest")
    @transaction.atomic
    def create_comment_to_quest(self, request):
        serializer = CommentQuestSerializer(data=request.data)
        data = func_is_valid_comment(request, serializer)
        return Response(data)

    @action(detail=False, methods=["get"], url_path="index/quest/<pk>")
    def index_comment_quest(self, request, pk):
        request = set_language_to_user(request)
        try:
            if not request.user.is_staff:
                if not Quest.objects.filter(
                    id=pk,
                    hide_to_user=False,
                    hide_to_moderator=False,
                    language=request.user.language,
                ):
                    raise Exception()

            comments = Comment.objects.filter(post=pk)
            if not comments:
                raise Exception()

            comments = CommentQuestShowSerializer(comments, many=True).data

            for comment in comments:
                comment["user"] = User.objects.get(id=comment["user"]).username

                if comment["delete_from_user"]:
                    comment["text"] = "This comment was deleted by the user."
        except Exception:
            raise Http404()

        return Response({"data": comments})

    @action(detail=True, methods=["get"], url_path="show/quest/<pk>")
    def show_comment_quest(self, request, pk):
        request = set_language_to_user(request)
        try:
            comment = get_object_or_404(Comment, id=pk)
            if not request.user.is_staff:
                if not Quest.objects.filter(
                    id=comment.post,
                    hide_to_user=False,
                    hide_to_moderator=False,
                    language=request.user.language,
                ):
                    raise Exception()

            comment = CommentQuestShowSerializer(comment).data

            if comment["delete_from_user"]:
                comment["text"] = "This comment was deleted by the user."

            comment["user"] = User.objects.get(id=comment["user"]).username

        except Exception:
            raise Http404()

        return Response({"data": comment})

    @action(detail=True, methods=["delete"], url_path="delete/<pk>")
    @transaction.atomic
    def delete_from_post(self, request, pk):
        try:
            comment = get_object_or_404(Comment, id=pk)
        except Exception:
            raise Http404()

        if comment.post:
            e = comment.post
        elif comment.survey:
            e = comment.survey
        else:
            e = None

        if e is not None:
            is_exp = opening_access(e, request.user)
            if (
                comment.user != request.user
                and not request.user.is_staff
                and e.user != request.user
            ):
                is_exp = True

            if is_exp:
                return Response({"detail": "forbidden for you."}, status=403)

        comment.delete()
        return Response({"success": "ok."})

    @action(detail=True, methods=["post"], url_path="delete_from_user/<pk>")
    @transaction.atomic
    def delete_from_user(self, request, pk):
        try:
            comment = get_object_or_404(Comment, id=pk)
            if comment.delete_from_user:
                raise Exception()
        except Exception:
            raise Http404()

        if comment.post:
            e = comment.post
        elif comment.survey:
            e = comment.survey

        is_exp = opening_access(e, request.user)
        if (
            comment.user != request.user
            and not request.user.is_staff
            and e.user != request.user
        ):
            is_exp = True

        if is_exp:
            return Response({"detail": "forbidden for you."}, status=403)

        comment.delete_from_user = True
        comment.save()
        return Response({"success": "ok.", "id": comment.id})


class AnswerViewSet(viewsets.GenericViewSet):
    queryset = Answer.objects.all()
    permission_classes = [IsAuthenticated, IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == "create_answer_to_post":
            return AnswerPostSerializer
        elif self.action == "create_answer_to_survey":
            return AnswerSurveySerializer
        elif self.action == "create_answer_to_test":
            return AnswerTestSerializer
        elif self.action == "create_answer_to_quest":
            return AnswerQuestSerializer
        elif self.action in ["index_answer_post", "show_answer_post"]:
            return AnswerPostShowSerializer
        elif self.action in ["index_answer_survey", "show_answer_survey"]:
            return AnswerSurveyShowSerializer
        elif self.action in ["index_answer_test", "show_answer_test"]:
            return AnswerTestShowSerializer
        elif self.action in ["index_answer_quest", "show_answer_quest"]:
            return AnswerQuestShowSerializer
        else:
            return AnswerFullSerializer

    @action(detail=True, methods=["post"], url_path="create/post")
    @transaction.atomic
    def create_answer_to_post(self, request):
        serializer = AnswerPostSerializer(data=request.data)
        data = func_is_valid_answer(request, serializer)

        post = Post.objects.get(id=request.data.get("post"))
        if opening_access(post, request.user):
            raise Http404()

        return Response(data)

    @action(detail=True, methods=["post"], url_path="create/survey")
    @transaction.atomic
    def create_answer_to_survey(self, request):
        serializer = AnswerSurveySerializer(data=request.data)
        data = func_is_valid_answer(request, serializer)

        survey = Survey.objects.get(id=request.data.get("survey"))
        if opening_access(survey, request.user):
            raise Http404()

        return Response(data)

    @action(detail=True, methods=["post"], url_path="create/test")
    @transaction.atomic
    def create_answer_to_test(self, request):
        data = {}

        serializer = AnswerTestSerializer(data=request.data)
        data = func_is_valid_answer(request, serializer)

        return Response(data)

    @action(detail=True, methods=["post"], url_path="create/quest")
    @transaction.atomic
    def create_answer_to_quest(self, request):
        data = {}

        serializer = AnswerQuestSerializer(data=request.data)
        data = func_is_valid_answer(request, serializer)

        return Response(data)

    @action(detail=False, methods=["get"], url_path="index/<pk>/post")
    def index_answer_post(self, request, pk):
        comment = get_object_or_404(Comment, id=pk)
        answers = get_list_or_404(Answer, comment=comment)

        if comment.post:
            e = get_object_or_404(Post, id=comment.post.pk)
            answers = AnswerPostShowSerializer(answers, many=True).data

        request = set_language_to_user(request)
        if opening_access(e, request.user):
            raise Http404()

        for answer in answers:
            answer["user"] = User.objects.get(id=answer["user"]).username

        return Response({"data": answers})

    @action(detail=False, methods=["get"], url_path="index/<pk>/survey")
    def index_answer_survey(self, request, pk):
        comment = get_object_or_404(Comment, id=pk)
        answers = get_list_or_404(Answer, comment=comment)

        if comment.survey:
            e = get_object_or_404(Survey, id=comment.survey.pk)
            answers = AnswerSurveyShowSerializer(answers, many=True).data

        request = set_language_to_user(request)
        if opening_access(e, request.user):
            raise Http404()

        for answer in answers:
            answer["user"] = User.objects.get(id=answer["user"]).username

        return Response({"data": answers})

    @action(detail=False, methods=["get"], url_path="index/<pk>/test")
    def index_answer_test(self, request, pk):
        comment = get_object_or_404(Comment, id=pk)
        answers = get_list_or_404(Answer, comment=comment)

        if comment.test:
            e = get_object_or_404(Test, id=comment.test.pk)
            answers = AnswerTestShowSerializer(answers, many=True).data

        # if opening_access(e, request.user):
        #     raise Http404()

        for answer in answers:
            answer["user"] = User.objects.get(id=answer["user"]).username

        return Response({"data": answers})

    @action(detail=False, methods=["get"], url_path="index/<pk>/quest")
    def index_answer_quest(self, request, pk):
        comment = get_object_or_404(Comment, id=pk)
        answers = get_list_or_404(Answer, comment=comment)

        if comment.quest:
            e = get_object_or_404(Quest, id=comment.quest.pk)
            answers = AnswerQuestShowSerializer(answers, many=True).data

        # if opening_access(e, request.user):
        #     raise Http404()

        for answer in answers:
            answer["user"] = User.objects.get(id=answer["user"]).username

        return Response({"data": answers})

    @action(detail=True, methods=["get"], url_path="show/<pk>/post")
    def show_answer_post(self, request, pk):
        answer = get_object_or_404(Answer, id=pk)

        if answer.post:
            e = get_object_or_404(Post, id=answer.post.pk)
            answer = AnswerPostShowSerializer(answer).data

        request = set_language_to_user(request)
        if opening_access(e, request.user):
            raise Http404()

        answer["user"] = User.objects.get(id=answer["user"]).username

        return Response({"data": answer})

    @action(detail=True, methods=["get"], url_path="show/<pk>/survey")
    def show_answer_survey(self, request, pk):
        answer = get_object_or_404(Answer, id=pk)

        if answer.survey:
            e = get_object_or_404(Survey, id=answer.survey.pk)
            answer = AnswerSurveyShowSerializer(answer).data

        request = set_language_to_user(request)
        if opening_access(e, request.user):
            raise Http404()

        answer["user"] = User.objects.get(id=answer["user"]).username

        return Response({"data": answer})

    @action(detail=True, methods=["get"], url_path="show/<pk>/test")
    def show_answer_test(self, request, pk):
        answer = get_object_or_404(Answer, id=pk)

        if answer.test:
            e = get_object_or_404(Post, id=answer.test.pk)
            answer = AnswerTestShowSerializer(answer).data

        # if opening_access(e, request.user):
        #     raise Http404()

        answer["user"] = User.objects.get(id=answer["user"]).username

        return Response({"data": answer})

    @action(detail=True, methods=["get"], url_path="show/<pk>/quest")
    def show_answer_quest(self, request, pk):
        answer = get_object_or_404(Answer, id=pk)

        if answer.quest:
            e = get_object_or_404(Quest, id=answer.quest.pk)
            answer = AnswerQuestShowSerializer(answer).data

        # if opening_access(e, request.user):
        #     raise Http404()

        answer["user"] = User.objects.get(id=answer["user"]).username

        return Response({"data": answer})

    @action(detail=True, methods=["delete"], url_path="delete/<pk>")
    @transaction.atomic
    def delete_answer(self, request, pk):
        if request.method == "DELETE":
            try:
                answer = get_object_or_404(Answer, pk=pk)
            except Exception:
                raise Http404()

            if answer.comment.post:
                e = answer.comment.post
            elif answer.comment.survey:
                e = answer.comment.survey

            is_exp = opening_access(e, request.user)
            if (
                answer.user != request.user
                and not request.user.is_staff
                and e.user != request.user
            ):
                is_exp = True

            if is_exp:
                return Response({"detail": "forbidden for you."}, status=403)

            answer.delete()
            return Response({"success": "ok."})
