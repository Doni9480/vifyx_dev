from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.core.paginator import Paginator
from contests.models import Contest
from contests.utils import E_DICT, M_DICT, get_jobs, P_DICT
from django.utils import timezone


def index(request):
    filter_kwargs = {'language': request.user.language}
    if request.user.language == 'any':
        del filter_kwargs['language']
    contests = Contest.objects.filter(**filter_kwargs)
    for contest in contests:
        contest.count_participants = E_DICT[contest.item_type].objects.filter(contest=contest).count()
    paginator = Paginator(contests, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, 'contests/index.html', {'page_obj': page_obj})

def show(request, slug):
    contest = get_object_or_404(Contest, slug=slug)
    if (contest.language != request.user.language and request.user.language != 'any'):
        raise Http404()
    
    present = timezone.now()
    
    button_show = True
    if request.user.is_anonymous or E_DICT[contest.item_type].objects.filter(contest=contest, user=request.user.id) or contest.end_date <= present or contest.start_date >= present:
        button_show = False
    count_participants = E_DICT[contest.item_type].objects.filter(contest=contest).count()
    
    if contest.item_type == 'post': filter_kwargs = {'level_access': None, 'user': request.user.id, 'is_paid': False, 'date__gte': contest.start_date}
    else: filter_kwargs = {'level_access': None, 'user': request.user, 'date__gte': contest.start_date}
    elements = M_DICT[contest.item_type].objects.filter(**filter_kwargs)
    
    prize = None
    if contest.is_end:
        prize = P_DICT[contest.item_type].objects.filter(contest=contest).first()
    
    paginator = Paginator(get_jobs(contest), 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
        
    return render(request, 'contests/show.html', {
        "contest": contest, 
        "count_participants": count_participants,
        "button_show": button_show,
        "elements": page_obj,
        "selects": elements,
        "prize": prize,
    })