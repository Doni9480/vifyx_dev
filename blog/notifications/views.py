from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from notifications.models import Notification


@login_required(login_url='/registration/login')
def index(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-date')
    count = 0
    notifications_dict = {}
    for notification in notifications:
        notifications_dict[count] = notification
        count += 1
    for key, value in notifications_dict.copy().items():
        if value.system_text:
            if not (request.user.language == 'russian' and value.system_text.russian) and \
            not (value.system_text.english and request.user.language != 'russian'):
                del notifications_dict[key]
    notifications = list(notifications_dict.values())
                                 
    paginator = Paginator(notifications, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, 'notifications/index.html', {'page_obj': page_obj})