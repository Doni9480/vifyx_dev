from django.urls import path
from users.views import *


urlpatterns = [
    path("registration/login/", login_register, name="login_register"),
    path("my/profile/", my_profile, name="my_profile"),
    path("profile/<str:username>/", profile, name="profile"),
    path("forgot_password/", forgot_password, name="forgot_password"),
    path("change_password/<uidb64>/<token>/", change_password, name="change_password"),
]
