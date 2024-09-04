from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from contests.models import Contest
from contests.utils import get_jobs, E_DICT, M_DICT, get_prize
from django.http import Http404
from contests.api.seriallzers import (
    ContestSerializer,
)
from django.utils import timezone
from blog.utils import MyPagination, set_language_to_user
from operator import attrgetter


class ContestViewSet(viewsets.ModelViewSet):
    queryset = Contest.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ContestSerializer
    permission_classes_by_action = dict.fromkeys(['list', 'retrieve'], [AllowAny])
    pagination_class = MyPagination
    
    def get_permissions(self):
        try:
            # return permission_classes depending on `action`
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            # action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]
        
    def list(self, request, *args, **kwargs):
        request = set_language_to_user(request)
        filter_kwargs = {'language': request.user.language}
        if request.user.language == 'any':
            del filter_kwargs['language']
        obj_set = sorted(Contest.objects.filter(**filter_kwargs), key=attrgetter('start_date'), reverse=True)
        contests = ContestSerializer(
            obj_set,
            many=True,
        ).data
        for contest in contests:
            contest['count_participants'] = E_DICT[contest['item_type']].objects.filter(contest=contest['id']).count()
        page = self.paginate_queryset(contests)
        return self.get_paginated_response(page)
    
    def retrieve(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        request = set_language_to_user(request)
        if (instance.language != request.user.language and request.user.language != 'any'):
            raise Http404()
        jobs = get_jobs(instance, is_api=True)
        contest = self.get_serializer(instance).data
        contest[contest['item_type'] + 's'] = jobs
        
        if instance.is_end:
            contest['results'] = get_prize(contest)

        contest['count_participants'] = len(jobs)
        return Response({"data": contest})
        
    @action(detail=True, methods=["post"], url_path="add_element/<pk>")
    def add_element(self, request, pk=None):
        contest = self.get_object()
        data = {}
        try:
            if contest.end_date <= timezone.now() or contest.start_date >= timezone.now():
                data['id'] = 'Contest is end.'
            elif E_DICT[contest.item_type].objects.filter(user=request.user):
                data['id'] = 'You have already added a job.'
            elif request.user.is_banned:
                data['id'] = 'You cannot participate in the contest.'
            else:
                if contest.item_type == 'post':
                    kwargs = {'id': int(request.data['id']), 'user': request.user, 'level_access': None, 'is_paid': False, 'date__gte': contest.start_date}
                else:
                    kwargs = {'id': int(request.data['id']), 'user': request.user, 'level_access': None, 'date__gte': contest.start_date}
                element = get_object_or_404(M_DICT[contest.item_type], **kwargs)
                kwargs = {contest.item_type: element, 'contest': contest, 'user': request.user}
                E_DICT[contest.item_type].objects.create(**kwargs)
                data['success'] = 'ok.'
        except (ValueError, KeyError) as e:
            data['id'] = 'Invalid id.'
        return Response(data)