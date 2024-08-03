from django.urls import re_path, path
from users.api.views import (
    RegisterViewSet,
    LoginViewSet,
    UserViewSet,
    ProfileViewSet,
)
from blog.routers import CustomRouter

router = CustomRouter()
router.register(r"", RegisterViewSet, basename="registration")
router.register(r"", LoginViewSet, basename="login")
router.register(r"", UserViewSet, basename="user")
router.register(r"", ProfileViewSet, basename="profile")


urlpatterns = router.urls

# urlpatterns = [
#     path("registration/", RegisterView.as_view()),
#     path("login/", LoginView.as_view()),
#     path("logout/", LogoutView.as_view()),
#     path("get_scores/", GetScoresView.as_view()),
#     path("send_scores_to_user/<int:id>/", SendScoresToUserView.as_view()),
#     path("forbid_to_comment/<int:id>/", ForbidToCommentView.as_view()),
#     path("forbid_to_post/<int:id>/", ForbidToPostView.as_view()),
#     path("allow_to_comment/<int:id>/", AllowToCommentView.as_view()),
#     path("allow_to_post/<int:id>/", AllowToPostView.as_view()),
#     path("my/profile/", MyProfileView.as_view()),
#     path("profile/<str:username>/", ProfileView.as_view()),
#     path("profile/posts/<str:username>/", PostsShowView.as_view()),
#     path("profile/surveys/<str:username>/", SurveysShowView.as_view()),
# ]
