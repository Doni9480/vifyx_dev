from django.urls import reverse
from django.http import Http404
from django.utils import timezone

from notifications.models import Notification

import zoneinfo
import pytz
import datetime


class AdminCheckMiddleware:
    def __init__(self, get_response):
        self._get_response = get_response

    def __call__(self, request):
        if request.path.startswith(reverse("admin:index")):
            if request.user.is_authenticated:
                if not request.user.is_staff:
                    raise Http404
            else:
                raise Http404

        response = self._get_response(request)
        return response


class TimezoneMiddleware:
    def __init__(self, get_response):
        self._get_response = get_response

    def __call__(self, request):
        try:
            # get django_timezone from cookie
            tzname = request.COOKIES.get("timezone")

            if tzname:
                timezone.activate(zoneinfo.ZoneInfo(tzname))

                utc_offset = str(
                    datetime.datetime.now(pytz.timezone(tzname)).utcoffset()
                )
                utc_offset = utc_offset.split(":")[0]
                request.user.utc_offset = int(utc_offset)
            else:
                timezone.deactivate()
                request.user.utc_offset = 0
        except Exception as e:
            timezone.deactivate()

        response = self._get_response(request)
        return response


class NotificationsMiddleware:
    def __init__(self, get_response):
        self._get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:            
            request.notifications = Notification.objects.filter(
                user=request.user, is_read=False,
            ).order_by('-date')[:5]

        response = self._get_response(request)
        return response


class LanguageMiddleware:
    def __init__(self, get_response):
        self._get_response = get_response
        
    def __call__(self, request):
        if not request.user.is_authenticated:
            request.user.language = 'any'
        response = self._get_response(request)
        return response