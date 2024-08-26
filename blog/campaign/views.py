from typing import Any
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from .models import Campaign, Task, UserTaskChecking, SubscriptionsCampaign
from .forms import CampaignForm, TaskForm
from django.conf import settings
from django.urls import reverse


class CampaignListView(ListView):
    paginate_by = 10
    model = SubscriptionsCampaign
    template_name = "campaign/list.html"

    def get_queryset(self):
        obj, created = SubscriptionsCampaign.objects.get_or_create(user=self.request.user)
        if created or obj.campaigns.count() == 0:
            sys_campaign = Campaign.objects.filter(user__username='system') or []
            if sys_campaign:
                obj.campaigns.add(*sys_campaign)
                obj.save()
        return obj.campaigns.all()
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["other_campaigns"] = Campaign.objects.all().exclude(pk__in=self.get_queryset())
        return context


class CampaignDetailView(DetailView):
    model = Campaign
    template_name = "campaign/detail.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["statistics"] = UserTaskChecking.getting_statistics(self.object.pk)
        return context


def campaign_create(request):
    if request.method == "POST":
        form = CampaignForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("campaign_list")
    else:
        form = CampaignForm()
    return render(
        request,
        "campaign/create.html",
        {
            "form": form,
            "recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
        },
    )


def campaign_update(request, slug):
    campaign = get_object_or_404(Campaign, slug=slug)
    if request.method == "POST":
        form = CampaignForm(request.POST, instance=campaign)
        if form.is_valid():
            form.save()
            return redirect("campaign_list")
    else:
        form = CampaignForm(instance=campaign)
    return render(
        request,
        "campaign/update.html",
        {
            "form": form,
            "campaign": campaign,
            "recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
        },
    )


# def campaign_delete(request, pk):
#     campaign = get_object_or_404(Campaign, pk=pk)
#     if request.method == "POST":
#         campaign.delete()
#         return redirect("campaign_list")
#     return render(request, "campaign.html", {"campaign": campaign})


# class TaskListView(ListView):
#     model = Task
#     template_name = "task.html"
#     context_object_name = "task"
class TaskListView(ListView):
    paginate_by = 10
    model = Task
    template_name = "task/list.html"

    def get_queryset(self):
        user_tasks = UserTaskChecking.objects.filter(
            user=self.request.user.pk
        ).values_list("task", flat=True)
        queryset = super().get_queryset()
        return queryset.exclude(pk__in=set(user_tasks))


class TaskDetailView(DetailView):
    model = Task
    template_name = "task/detail.html"


def task_create(request, slug):
    # if request.method == "POST":
    #     form = TaskForm(request.POST)
    #     # if form.is_valid():
    #     #     form.save()
    #     #     return redirect("task_list")
    # else:
    obj = get_object_or_404(Campaign, slug=slug)
    redirect_url = reverse("campaign_detail", kwargs={"slug": obj.slug})
    campaign_pk = obj.pk
    form = TaskForm()
    return render(
        request,
        "task/create.html",
        {
            "form": form,
            "campaign_pk": campaign_pk,
            "redirect_url": redirect_url,
            "recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
        },
    )


def task_update(request, slug, pk):
    task = get_object_or_404(Task, pk=pk)
    obj = get_object_or_404(Campaign, slug=slug)
    # if request.method == "POST":
    #     form = TaskForm(request.POST, instance=task)
    #     if form.is_valid():
    #         form.save()
    #         return redirect("task_list")
    # else:
    redirect_url = reverse("campaign_detail", kwargs={"slug": obj.slug})
    campaign_pk = obj.pk
    task_pk = task.pk
    form = TaskForm(instance=task)
    return render(
        request,
        "task/update.html",
        {
            "form": form,
            "task_pk": task_pk,
            "campaign_pk": campaign_pk,
            "redirect_url": redirect_url,
            "recaptcha_site_key": settings.GOOGLE_RECAPTCHA_PUBLIC_KEY,
        },
    )


# def task_delete(request, pk):
#     task = get_object_or_404(Task, pk=pk)
#     if request.method == "POST":
#         task.delete()
#         return redirect("task_list")
#     return render(request, "task.html", {"task": task})
