from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from notifications.models import Notification

@login_required(login_url='/registration/login')
def index(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-date')
    paginator = Paginator(notifications, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'notifications/index.html', {'page_obj': page_obj})