from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser


from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404

from users.api.serializers import *
from users.api.utils import delete_token
from users.models import User, Percent

from blogs.models import Blog, PaidFollow, BlogFollow

from users.api.serializers import BlogFollowSerializer


class RegisterViewSet(viewsets.GenericViewSet):
    serializer_class = RegisterSerializer
    # parser_classes = [MultiPartParser, FormParser]

    @action(detail=True, methods=["post"], url_path="registration")
    @transaction.atomic
    def create_account(self, request):

        serializer = RegisterSerializer(data=request.data)

        data = {}
        if serializer.is_valid():
            serializer.save()

            token = serializer.generate_key()

            data["response"] = "Successful registered a new user."
            data["token"] = token
        else:
            data = serializer.errors

        return Response(data)


class LoginViewSet(viewsets.GenericViewSet):
    serializer_class = LoginSerializer

    @action(detail=True, methods=["post"], url_path="login")
    @transaction.atomic
    def login(self, request):
        data = {}
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.generate_key()
            data["response"] = "You have successfully logged in."
            data["token"] = token
        else:
            data = serializer.errors

        return Response(data)


class UserViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        # if self.action != 'logout':
        return [permission() for permission in self.permission_classes]

    @action(detail=False, methods=["post"])
    @transaction.atomic
    def logout(self, request):
        delete_token(request.user)
        return Response({"response": "You have logged out of your account."})

    @action(detail=False, methods=["post"])
    @transaction.atomic
    def get_scores(self, request):
        if request.user.unearned_scores == 0:
            raise Http404()

        user = request.user
        user.scores += user.unearned_scores
        user.unearned_scores = 0
        user.save()

        data = {
            "response": "success",
            "scores": user.scores,
        }

        return Response(data)

    @action(detail=True, methods=["post"], url_path=r"(?P<id>\d+)/send_scores_to_user")
    @transaction.atomic
    def send_scores_to_user(self, request, id=None):
        data = {}

        user = get_object_or_404(User, id=id)
        if user == request.user:
            raise Http404()

        serializer = ScoresSerializer(data=request.data)

        if serializer.is_valid():
            _user = request.user
            admin = User.objects.filter(is_superuser=True).first()
            if _user == admin:
                _user = admin

            scores = int(serializer.validated_data["scores"])
            if _user.scores < scores:
                data["error_scores"] = "you have fewer scores than you indicated."
            elif scores <= 0:
                data["error_scores"] = "you cannot enter a negative value."
            else:
                _user.scores -= scores
                _user.save()

                percent = Percent.objects.all()[0].percent / 100
                admin.scores += int(scores * percent) or 1
                admin.save()

                reverse_percent = 1 - Percent.objects.all()[0].percent / 100
                scores = int(scores * reverse_percent) or 1

                user.scores += scores
                user.save()

                data["success"] = "ok."
                data["scores"] = user.scores
        else:
            data = serializer.errors

        return Response(data)

    @action(detail=True, methods=["post"], url_path=r"forbid_to_post/(?P<id>\d+)")
    @transaction.atomic
    def forbid_to_post(self, request, id=None):
        try:
            user = get_object_or_404(User, id=id)
            if not request.user.is_staff:
                raise Exception()
        except Exception:
            raise Http404()

        data = {}

        user.is_published_post = False
        user.save()

        data["success"] = "ok."

        return Response(data)

    @action(detail=True, methods=["post"], url_path=r"forbid_to_comment/(?P<id>\d+)")
    @transaction.atomic
    def forbid_to_comment(self, request, id=None):
        try:
            user = get_object_or_404(User, id=id)
            if not request.user.is_staff:
                raise Exception()
        except Exception:
            raise Http404()
        data = {}
        user.is_published_comment = False
        user.save()
        data["success"] = "ok."
        return Response(data)

    @action(detail=True, methods=["post"], url_path=r"allow_to_post/(?P<id>\d+)")
    @transaction.atomic
    def allow_to_post(self, request, id=None):
        try:
            user = get_object_or_404(User, id=id)
            if not request.user.is_staff:
                raise Exception()
        except Exception:
            raise Http404()

        data = {}

        user.is_published_post = True
        user.save()

        data["success"] = "ok."

        return Response(data)

    @action(detail=True, methods=["post"], url_path=r"allow_to_comment/(?P<id>\d+)")
    @transaction.atomic
    def allow_to_comment(self, request, id=None):
        try:
            user = get_object_or_404(User, id=id)
            if not request.user.is_staff:
                raise Exception()
        except Exception:
            raise Http404()

        if request.method == "POST":
            data = {}

            user.is_published_comment = True
            user.save()

            data["success"] = "ok."

            return Response(data)

    @action(detail=True, methods=["post"], url_path="is_notificated")
    @transaction.atomic
    def is_notificated(self, request, *args, **kwargs):
        data = {}

        is_notificated = request.data.get("is_notificated", False)
        user = request.user
        if is_notificated == "true":
            user.is_notificated = True
        elif is_notificated == "false":
            user.is_notificated = False
        user.save()

        return Response(data)

    @action(detail=True, methods=["post"], url_path="is_autorenewal")
    @transaction.atomic
    def is_autorenewal(self, request):
        data = {}

        is_autorenewal = request.data.get("is_autorenewal", False)
        user = request.user
        if is_autorenewal == "true":
            user.is_autorenewal = True
        elif is_autorenewal == "false":
            user.is_autorenewal = False
        user.save()

        return Response(data)
    
    @action(detail=True, methods=["post"], url_path="set_language")
    @transaction.atomic
    def set_language(self, request, language=None):
        language = request.data['language']
        if language in ['russian', 'english', 'any']:
            request.user.language = language
            request.user.save()
            return Response({'success': 'ok.'})

        return Response(
            {"language": "Invalid language (valid: russian, english, any)"}, status=status.HTTP_400_BAD_REQUEST
        )
class ProfileViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"])
    def my_profile(self, request):
        blogs = BlogSerializer(Blog.objects.filter(user=request.user), many=True).data

        follows = BlogFollowSerializer(
            BlogFollow.objects.filter(follower=request.user), many=True
        ).data
        for follow in follows:
            follow["user"] = User.objects.get(id=follow["user"]).username
        
        paid_follow_models = PaidFollow.objects.filter(follower=request.user)
        paid_follows = []
        for paid_follow_model in paid_follow_models:
            paid_follows.append(BlogSerializer(paid_follow_model.blog).data)

        data = {
            "blogs": blogs,
            "paid_follows": paid_follows,
            "follows": follows,
        }

        return Response({"data": data})

    @action(detail=True, methods=["get"], url_path=r"(?P<username>[^/.]+)/profile")
    def profile(self, request, username=None):
        user = get_object_or_404(User, username=username)
        blogs = BlogSerializer(Blog.objects.filter(user=user), many=True).data

        return Response({"data": {"user": user.username, "blogs": blogs}})


# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated

# from django.db import transaction
# from django.http import Http404
# from django.shortcuts import get_object_or_404

# from users.api.serializers import (
#     LoginSerializer,
#     ScoresSerializer,
#     SurveysSerializer,
#     PostsSerializer,
# )
# from users.api.utils import delete_token
# from users.models import Token, User

# from posts.models import Post, View

# from surveys.models import Survey, View as View_survey

# from comments.models import Comment, Answer

# from blog.utils import check_recaptcha
# from blog.decorators import recaptcha_checking


# class RegisterView(APIView):

#     @recaptcha_checking
#     @transaction.atomic
#     def post(self, request):
#         data = {}
#         serializer = LoginSerializer(data=request.data)

#         if serializer.is_valid():
#             token = serializer.generate_key()
#             data["response"] = "You have successfully logged in."
#             data["token"] = token
#         else:
#             data = serializer.errors
#         return Response(data)


# class LoginView(APIView):

#     @recaptcha_checking
#     @transaction.atomic
#     def post(self, request):
#         data = {}
#         serializer = LoginSerializer(data=request.data)

#         if serializer.is_valid():
#             token = serializer.generate_key()
#             data["response"] = "You have successfully logged in."
#             data["token"] = token
#         else:
#             data = serializer.errors
#         return Response(data)


# class LogoutView(APIView):
#     permission_classes = [IsAuthenticated]

#     @transaction.atomic
#     def post(self, request):
#         delete_token(request.user)
#         return Response({"response": "You have logged out of your account."})


# class GetScoresView(APIView):
#     permission_classes = [IsAuthenticated]

#     @transaction.atomic
#     def post(self, request):
#         if request.user.unearned_scores == 0:
#             raise Http404()

#         user = request.user
#         user.scores += user.unearned_scores
#         user.unearned_scores = 0
#         user.save()

#         data = {
#             "response": "success",
#             "scores": user.scores,
#         }

#         return Response(data)


# class SendScoresToUserView(APIView):
#     permission_classes = [IsAuthenticated]

#     @recaptcha_checking
#     @transaction.atomic
#     def post(self, request, id):
#         data = {}

#         try:
#             user = get_object_or_404(User, id=id)
#             if user == request.user:
#                 raise Exception()
#         except Exception:
#             raise Http404()

#         serializer = ScoresSerializer(data=request.data)

#         if serializer.is_valid():
#             _user = request.user

#             scores = int(serializer.validated_data["scores"])
#             _user.scores -= scores
#             if _user.scores < 0:
#                 data["error_scores"] = "you have fewer scores than you indicated."
#             elif scores <= 0:
#                 data["error_scores"] = "you cannot enter a negative value."
#             else:
#                 _user.save()

#                 admin = User.objects.filter(is_superuser=True)[0]
#                 admin.scores += int(scores * 0.3) or 1
#                 admin.save()

#                 scores = int(scores * 0.7) or 1

#                 user.scores += scores
#                 user.save()

#                 data["success"] = "ok."
#                 data["scores"] = user.scores
#         else:
#             data = serializer.errors

#         return Response(data)


# class ForbidToPostView(APIView):
#     permission_classes = [IsAuthenticated]

#     @transaction.atomic
#     def post(self, request, id):
#         user = get_object_or_404(User, id=id)
#         if not request.user.is_staff:
#             raise Http404()

#         data = {}

#         user.is_published_post = False
#         user.save()

#         data["success"] = "ok."

#         return Response(data)


# class ForbidToCommentView(APIView):
#     permission_classes = [IsAuthenticated]

#     @transaction.atomic
#     def post(self, request, id):
#         user = get_object_or_404(User, id=id)
#         if not request.user.is_staff:
#             raise Http404()

#         data = {}

#         user.is_published_comment = False
#         user.save()

#         data["success"] = "ok."

#         return Response(data)


# class AllowToPostView(APIView):
#     permission_classes = [IsAuthenticated]

#     @transaction.atomic
#     def post(self, request, id):
#         user = get_object_or_404(User, id=id)
#         if not request.user.is_staff:
#             raise Http404()

#         data = {}

#         user.is_published_post = True
#         user.save()

#         data["success"] = "ok."

#         return Response(data)


# class AllowToCommentView(APIView):
#     permission_classes = [IsAuthenticated]

#     @transaction.atomic
#     def post(self, request, id):
#         user = get_object_or_404(User, id=id)
#         if not request.user.is_staff:
#             raise Http404()
#         data = {}

#         user.is_published_comment = True
#         user.save()

#         data["success"] = "ok."

#         return Response(data)


# class MyProfileView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         surveys = Survey.objects.filter(user=request.user).order_by("-date")[:3]
#         surveys = SurveysSerializer(surveys, many=True).data
#         for survey in surveys:
#             count_comments = Comment.objects.filter(survey=survey["id"]).count()
#             count_answers = Answer.objects.filter(survey=survey["id"]).count()
#             count_comments = count_comments + count_answers
#             survey["count_comments"] = count_comments

#             survey["count_views"] = View_survey.objects.filter(
#                 survey=survey["id"]
#             ).count()

#             survey["user"] = User.objects.get(id=survey["user"]).username

#         posts = Post.objects.filter(user=request.user).order_by("-date")[:3]
#         posts = PostsSerializer(posts, many=True).data
#         for post in posts:
#             count_comments = Comment.objects.filter(post=post["id"]).count()
#             count_answers = Answer.objects.filter(post=post["id"]).count()
#             count_comments = count_comments + count_answers
#             post["count_comments"] = count_comments

#             post["count_surveys"] = View.objects.filter(post=post["id"]).count()

#             post["user"] = User.objects.get(id=post["user"]).username

#         return Response({"data": {"posts": posts, "surveys": surveys}})


# class ProfileView(APIView):

#     def get(self, request, username):
#         user = get_object_or_404(User, username=username)

#         if not request.user.is_staff:
#             surveys = Survey.objects.filter(
#                 user=user,
#                 hide_to_user=False,
#                 hide_to_moderator=False,
#                 language=request.user.language,
#             ).order_by("-date")[:3]
#             posts = Post.objects.filter(
#                 user=user,
#                 hide_to_user=False,
#                 hide_to_moderator=False,
#                 language=request.user.language,
#             ).order_by("-date")[:3]
#         else:
#             surveys = Survey.objects.filter(
#                 user=user, language=request.user.language
#             ).order_by("-date")[:3]
#             posts = Post.objects.filter(
#                 user=user, language=request.user.language
#             ).order_by("-date")[:3]

#         surveys = SurveysSerializer(surveys, many=True).data
#         posts = PostsSerializer(posts, many=True).data

#         for survey in surveys:
#             count_comments = Comment.objects.filter(survey=survey["id"]).count()
#             count_answers = Answer.objects.filter(survey=survey["id"]).count()
#             count_comments = count_comments + count_answers
#             survey["count_comments"] = count_comments

#             survey["count_views"] = View_survey.objects.filter(
#                 survey=survey["id"]
#             ).count()

#             survey["user"] = User.objects.get(id=survey["user"]).username

#         for post in posts:
#             count_comments = Comment.objects.filter(post=post["id"]).count()
#             count_answers = Answer.objects.filter(post=post["id"]).count()
#             count_comments = count_comments + count_answers
#             post["count_comments"] = count_comments

#             post["count_surveys"] = View.objects.filter(post=post["id"]).count()

#             post["user"] = User.objects.get(id=post["user"]).username

#         return Response({"data": {"posts": posts, "surveys": surveys}})


# class PostsShowView(APIView):

#     def get(self, request, username):
#         try:
#             user = get_object_or_404(User, username=username)
#             if not request.user.is_staff:
#                 posts = Post.objects.filter(
#                     user=user,
#                     hide_to_user=False,
#                     hide_to_moderator=False,
#                     language=request.user.language,
#                 )
#             else:
#                 posts = Post.objects.filter(user=user, language=request.user.language)

#             if not posts:
#                 raise Exception()
#         except Exception:
#             raise Http404()


# class SurveysShowView(APIView):

#     def get(self, request, username):
#         try:
#             user = get_object_or_404(User, username=username)
#             if not request.user.is_staff:
#                 surveys = Survey.objects.filter(
#                     user=user,
#                     hide_to_user=False,
#                     hide_to_moderator=False,
#                     language=request.user.language,
#                 )
#             else:
#                 surveys = Survey.objects.filter(
#                     user=user, language=request.user.language
#                 )

#             if not surveys:
#                 raise Exception()
#         except Exception:
#             raise Http404()

#         surveys = SurveysSerializer(surveys, many=True).data
#         for survey in surveys:
#             count_comments = Comment.objects.filter(survey=survey["id"]).count()
#             count_answers = Answer.objects.filter(survey=survey["id"]).count()
#             count_comments = count_comments + count_answers
#             survey["count_comments"] = count_comments

#             count_views = View_survey.objects.filter(survey=survey["id"]).count()
#             survey["count_views"] = count_views

#             survey["user"] = User.objects.get(id=survey["user"]).username

#         return Response({"data": surveys})