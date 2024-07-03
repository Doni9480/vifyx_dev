from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes
from django.conf import settings
from django.forms import ValidationError

from users.models import User, TotalScore


def get_info(request, user):
    current_site = get_current_site(request)
    context = {
        "user": user,
        "domain": current_site.domain,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": default_token_generator.make_token(user),
    }
    return context


def send_email_for_change(request, user):
    context = get_info(request, user)
    mail_from = settings.EMAIL_FROM
    message = render_to_string("change_verify_email.html", context=context)

    email = EmailMessage("Password change", message, mail_from, to=[user.email])
    email.send()


def get_user(uidb64):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist, ValidationError):
        user = None
    return user


def send_scores():
    users = User.objects.all()
    if users:
        _total_scores = TotalScore.objects.all()
        if _total_scores:
            scores = _total_scores[0].scores
            for user in users:
                user.unearned_scores = scores
                user.save()
