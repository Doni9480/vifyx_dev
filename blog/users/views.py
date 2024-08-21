from django.shortcuts import render, redirect
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from campaign.models import Campaign, Task, UserTaskChecking
from users.forms import ChangeEmailForm, PasswordChangeForm
from users.models import User, TotalScore, Hide
from users.utils import send_email_for_change, get_user

from blogs.models import Blog, PaidFollow, BlogFollow

from blog.utils import check_recaptcha
from periodic_bonuses.models import PeriodicBonuses
from periodic_bonuses.api.serializers import PeriodicBonusesSerializer

# from unfold.admin import AdminView


def login_register(request):
    if request.user.is_authenticated:
        raise Http404("Page not found")
    return render(
        request,
        "login-register.html",
        {"recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY},
    )


def forgot_password(request):
    if request.user.is_authenticated:
        raise Http404("Page not found")

    if request.method == "POST":
        request = check_recaptcha(request)
        if request.recaptcha_is_valid:

            form = ChangeEmailForm(request.POST)

            if form.is_valid():
                email = form.cleaned_data["email"]
                user = User.objects.get(email=email)
                send_email_for_change(request, user)
                messages.success(request, "The letter was sent to the email address.")
                return HttpResponseRedirect(reverse("forgot_password"))
        else:
            messages.error(request, "Invalid recaptcha.")
            form = ChangeEmailForm()
    else:
        form = ChangeEmailForm()

    return render(
        request,
        "forgot_password.html",
        {"form": form, "recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY},
    )


@transaction.atomic
def change_password(request, uidb64, token):
    if not request.user.is_authenticated:
        user = get_user(uidb64)  # get a user
        if user is not None and default_token_generator.check_token(
            user, token
        ):  # проверка токена
            if request.method == "POST":
                request = check_recaptcha(request)
                if request.recaptcha_is_valid:

                    form = PasswordChangeForm(request.POST)

                    if form.is_valid():
                        user.set_password(form.cleaned_data["password"])
                        user.save()
                        messages.success(
                            request,
                            "Your password has been changed. Please log in with the new password.",
                        )
                        return HttpResponseRedirect(reverse("login_register"))
                else:
                    messages.success(request, "Invalid recaptcha.")
            else:
                form = PasswordChangeForm()

            return render(
                request,
                "change_password.html",
                {
                    "form": form,
                    "recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
                },
            )

    raise Http404()


@login_required(login_url="/registration/login")
def my_profile(request):
    bonuses_list = PeriodicBonuses.objects.all()
    periudic_bonuses = list(
        PeriodicBonusesSerializer(
            instance=bonuses_list, many=True, context={"request": request}
        ).data
    )
    completed_tasks = UserTaskChecking.objects.filter(
        user=request.user, is_completed=True, is_received=False
    )
    blogs = Blog.objects.filter(user=request.user)
    follows = BlogFollow.objects.filter(follower=request.user)
    companies = Campaign.objects.filter(user=request.user)
    paid_follows = PaidFollow.objects.filter(follower=request.user)
    muted = Hide.objects.filter(hider=request.user)

    total_scores = TotalScore.objects.all()[0]
    if len(str(total_scores.minute)) == 1:
        total_scores.minute = "0" + str(total_scores.minute)

    data = {
        "periudic_bonuses": periudic_bonuses,
        "completed_tasks": completed_tasks,
        "blogs": blogs,
        "companies": companies,
        "muted": muted,
        "follows": follows,
        "paid_follows": paid_follows,
        "hour": total_scores.hour + request.user.utc_offset,
        "minute": total_scores.minute,
        "recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
    }

    return render(request, "my_profile.html", data)


def profile(request, username):
    user = get_object_or_404(User, username=username)

    if request.user == user:
        return redirect("users:my_profile")

    blogs = Blog.objects.filter(user=user)

    data = {
        "user": user,
        "blogs": blogs,
        "recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
    }

    return render(request, "profile.html", data)


def edit_profile(request):
    return render(request, "edit_profile.html")


def edit_password(request):
    return render(request, "edit_password.html")


# class MyCustomPage(AdminView):
#     template_name = "admin/custom/index.html"
#     page_title = "Моя кастомная страница"
#     page_description = "Описание моей кастомной страницы"

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["extra_data"] = "Дополнительные данные для отображения"
#         return context

def change_user_status(request, pk):
    if request.user.is_superuser:
        user = get_object_or_404(User, pk=pk)
        if user.is_active:
            user.is_active = False
            user.save()
        else:
            user.is_active = True
            user.save()
        return Response({'success': True}, status=200)
    return Response({'success': False}, status=403)