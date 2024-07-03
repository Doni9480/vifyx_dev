import uuid
import os
import requests
import datetime
import calendar

from django.conf import settings


def my_custom_upload_to_func(instance, filename):
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join("uploads_summernote", filename)


def check_recaptcha(request):
    if (
        request.method == "POST"
        or request.method == "PATCH"
        or request.method == "DELETE"
    ):
        # API or classic request
        recaptcha_response = request.POST.get(
            "g_recaptcha_response"
        ) or request.data.get("g_recaptcha_response")

        data = {
            "secret": settings.GOOGLE_RECAPTCHA_PRIVATE_KEY,
            "response": recaptcha_response,
        }
        r = requests.post("https://www.google.com/recaptcha/api/siteverify", data=data)
        result = r.json()
        if result["success"]:
            request.recaptcha_is_valid = True
        else:
            request.recaptcha_is_valid = False

    return request


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)
