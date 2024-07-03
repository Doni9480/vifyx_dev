from blog.utils import check_recaptcha
from rest_framework import status
from rest_framework.response import Response


def recaptcha_checking(func):
    def wrapper(request, *args, **kwargs):
        request = check_recaptcha(request)
        if request.recaptcha_is_valid:
            return func(request, *args, **kwargs)
        else:
            data = {"recaptcha": "Invalid recaptcha."}
            return Response(data, status=status.HTTP_403_FORBIDDEN)

    return wrapper
