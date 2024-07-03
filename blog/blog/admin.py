from django.http import Http404, HttpResponseRedirect
from django.urls import reverse

from users.api.utils import delete_token


def login(request):
    raise Http404()

def logout(request):
    if request.method == 'POST':
        delete_token(request.user)
        
        response = HttpResponseRedirect(reverse('login_register'))
        response.set_cookie(request.resolver_match.app_name + 'blog_access_token', '', max_age=0)
        return response
    else:
        raise Http404()
    