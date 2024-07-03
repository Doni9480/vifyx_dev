from users.models import Token, User


class AuthTokenMiddleware:
    def __init__(self, get_response):
        self._get_response = get_response

    def __call__(self, request):
        access_token = ""
        if "Authorization" in request.headers:
            access_token = request.headers["Authorization"][6:]
        elif "blog_access_token" in request.COOKIES:
            access_token = request.COOKIES["blog_access_token"]

        if access_token:
            user_token = Token.objects.filter(key=access_token)
            if user_token:
                user = User.objects.get(id=user_token.get().user_id)
                request.user = user

        response = self._get_response(request)
        return response
