from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser

from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from users.api.serializers import *
from users.api.utils import delete_token
from users.models import User, Percent, Hide
from blogs.models import Blog, PaidFollow, BlogFollow
from users.api.serializers import BlogFollowSerializer, HideSerializer, EditProfileSerializer, EditPasswordSerializer
from notifications.models import Notification, Ban, Unban
from users.api.utils import N_DICT
from referrals.api.utils import ReferralHandler


class RegisterViewSet(viewsets.GenericViewSet):
    serializer_class = RegisterSerializer
    # parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "referral_code",
                openapi.IN_QUERY,
                description="Уникальный реферальный код",
                type=openapi.TYPE_STRING,
            )
        ]
    )
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
            
            if "referral_code" in request.query_params.keys():
                referral = ReferralHandler(request)
                print(serializer.data)
                data["referral"] = referral.save(dict(serializer.data))
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
        user = get_object_or_404(User, id=id)
        if not request.user.is_staff:
            raise Http404()

        data = {}

        user.is_published_post = False
        user.save()

        data["success"] = "ok."

        return Response(data)

    @action(detail=True, methods=["post"], url_path=r"forbid_to_comment/(?P<id>\d+)")
    @transaction.atomic
    def forbid_to_comment(self, request, id=None):
        user = get_object_or_404(User, id=id)
        if not request.user.is_staff:
            raise Http404()
        data = {}
        user.is_published_comment = False
        user.save()
        data["success"] = "ok."
        return Response(data)

    @action(detail=True, methods=["post"], url_path=r"allow_to_post/(?P<id>\d+)")
    @transaction.atomic
    def allow_to_post(self, request, id=None):
        user = get_object_or_404(User, id=id)
        if not request.user.is_staff:
            raise Http404()

        data = {}

        user.is_published_post = True
        user.save()

        data["success"] = "ok."

        return Response(data)

    @action(detail=True, methods=["post"], url_path=r"allow_to_comment/(?P<id>\d+)")
    @transaction.atomic
    def allow_to_comment(self, request, id=None):
        user = get_object_or_404(User, id=id)
        if not request.user.is_staff:
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
        language = request.data["language"]
        if language in ["russian", "english", "any"]:
            request.user.language = language
            request.user.save()
            return Response({"success": "ok."})

        return Response(
            {"language": "Invalid language (valid: russian, english, any)"},
            status=status.HTTP_400_BAD_REQUEST,
        )
        
    @action(detail=True, methods=["post"], url_path=r"select_category/(?P<namespace>[^/.]+)/(?P<id>\d+)")
    @transaction.atomic
    def select_category(self, request, namespace=None, id=None):        
        if namespace not in N_DICT: raise Http404()
        
        category_model = get_object_or_404(N_DICT[namespace]['model'], id=id)
        setattr(request.user, N_DICT[namespace]['user_category'], category_model)
        request.user.save()
        subcategories = N_DICT[namespace]['user_subcategory'].objects.filter(user=request.user)
        for deleted_subcategory in subcategories:
            deleted_subcategory.delete()
        return Response({'success': 'ok.'})
    
    @action(detail=True, methods=["post"], url_path=r"select_subcategory/(?P<namespace>[^/.]+)/(?P<id>\d+)/(?P<id_delete>\d+)")
    @transaction.atomic
    def select_subcategory(self, request, namespace=None, id=None, id_delete=None):
        if namespace not in N_DICT: raise Http404()
        
        if int(id_delete) > 0:
            get_object_or_404(N_DICT[namespace]['user_subcategory'], id=id_delete, user=request.user).delete()
        subcategory = get_object_or_404(N_DICT[namespace]['subcategory'], id=id)
        if not N_DICT[namespace]['user_subcategory'].objects.filter(subcategory=subcategory, user=request.user):
            N_DICT[namespace]['user_subcategory'].objects.create(subcategory=subcategory, user=request.user)
        return Response({'success': 'ok.'})
    
    @action(detail=False, methods=["post"], url_path=r"destroy_category/(?P<namespace>[^/.]+)")
    @transaction.atomic
    def destroy_category(self, request, namespace=None, *args, **kwargs):
        deleted_subcategories = N_DICT[namespace]['user_subcategory'].objects.filter(user=request.user)
        for deleted_subcategory in deleted_subcategories:
            deleted_subcategory.delete()
        setattr(request.user, N_DICT[namespace]['user_category'], None)
        request.user.save()
        return Response({'success': 'ok.'})


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

        muted = HideSerializer(Hide.objects.filter(user=request.user), many=True).data
        for hide in muted:
            hide["user"] = User.objects.get(id=hide["user"]).username

        data = {
            "blogs": blogs,
            "paid_follows": paid_follows,
            "follows": follows,
            "muted": muted,
        }

        return Response({"data": data})

    @action(detail=True, methods=["get"], url_path=r"(?P<username>[^/.]+)/profile")
    def profile(self, request, username=None):
        user = get_object_or_404(User, username=username)
        blogs = BlogSerializer(Blog.objects.filter(user=user), many=True).data

        return Response({"data": {"user": user.username, "blogs": blogs}})

    @action(
        detail=True, methods=["post"], url_path=r"(?P<username>[^/.]+)/hide_from_user"
    )
    def hide_from_user(self, request, username=None):
        user = get_object_or_404(User, username=username)
        if not (
            Hide.objects.filter(hider=request.user, user=user) or user == request.user
        ):
            Hide.objects.create(user=user, hider=request.user)
        return Response({"success": "ok."})

    @action(
        detail=True, methods=["post"], url_path=r"(?P<username>[^/.]+)/show_from_user"
    )
    def show_from_user(self, request, username=None):
        user = get_object_or_404(User, username=username)
        hide = Hide.objects.filter(hider=request.user, user=user)
        if hide:
            hide.first().delete()
        return Response({"success": "ok."})

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def connect_twitter_account(self, request):
        serializer = TwitterAccountUserSerializer(
            data=request.data, instance=request.user, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"response": "You have successfully connected your Twitter account."}
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def disconnect_twitter_account(self, request):
        user_obj = request.user
        user_obj.twitter = None
        user_obj.save()
        return Response(
            {"response": "You have successfully disconnected your Twitter account."}
        )

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def connect_telegram_wallet(self, request):
        serializer = TelegramWalletUserSerializer(
            data=request.data, instance=request.user, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"response": "You have successfully connected your Telegram Wallet."}
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    @transaction.atomic
    def disconnect_telegram_wallet(self, request):
        user_obj = request.user
        user_obj.telegram_wallet = None
        user_obj.save()
        return Response(
            {"response": "You have successfully disconnected your Twitter account."}
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

    @action(detail=False, methods=["patch"], url_path="edit_profile")
    def edit_profile(self, request):
        data = {}
        serializer = EditProfileSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            data["success"] = "ok."
        else:
            data = serializer.errors
        return Response(data)
    
    @action(detail=False, methods=["patch"], url_path="edit_password")
    def edit_password(self, request):
        data = {}
        serializer = EditPasswordSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            data["success"] = "ok."
        else:
            data = serializer.errors
        return Response(data)
    
    @action(detail=True, methods=["post"], url_path=r"banning/(?P<id>\d+)")
    @transaction.atomic
    def banning(self, request, id=None):
        user = get_object_or_404(User, id=id)
        if not request.user.is_staff:
            raise Http404()
        data = {}
        user.is_banned = True
        user.save()
        ban = Ban.objects.create()
        Notification.objects.create(ban=ban, user=user)
        
        data["success"] = "ok."
        return Response(data)

    @action(detail=True, methods=["post"], url_path=r"unbanning/(?P<id>\d+)")
    @transaction.atomic
    def unbanning(self, request, id=None):
        user = get_object_or_404(User, id=id)
        if not request.user.is_staff:
            raise Http404()
        data = {}
        user.is_banned = False
        user.save()
        unban = Unban.objects.create()
        Notification.objects.create(unban=unban, user=user)
        
        data["success"] = "ok."
        return Response(data)
    