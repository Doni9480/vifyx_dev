from posts.models import Post, PostView, PostLike
from posts.api.serializers import PostShowSerializer
from quests.models import Quest, QuestView, QuestLike
from quests.api.serializers import QuestSerializer
from albums.models import Album, AlbumView, AlbumLike
from albums.api.serializers import AlbumShowSerializer
from contests.models import PostElement, AlbumElement, QuestElement, PrizePostElement, PrizeAlbumElement, PrizeQuestElement
from posts.utils import get_more_to_posts
from posts.api.utils import get_more_to_posts as api_get_more_to_posts
from quests.utils import get_more_to_quests
from quests.api.utils import get_more_to_quests as api_get_more_to_quests
from albums.utils import get_more_to_albums
from albums.api.utils import get_more_to_albums as api_get_more_to_albums
from contests.models import Contest
from django.utils import timezone
from notifications.models import Notification
import operator


E_DICT = {'post': PostElement, 'quest': QuestElement, 'album': AlbumElement}
M_DICT = {'post': Post, 'quest': Quest, 'album': Album}
S_DICT = {'post': PostShowSerializer, 'quest': QuestSerializer, 'album': AlbumShowSerializer}
F_DICT = {'post': get_more_to_posts, 'quest': get_more_to_quests, 'album': get_more_to_albums}
P_DICT = {'post': PrizePostElement, 'quest': PrizeQuestElement, 'album': PrizeAlbumElement}
L_DICT = {'post': PostLike, 'quest': QuestLike, 'album': AlbumLike}
API_F_DICT = {'post': api_get_more_to_posts, 'quest': api_get_more_to_quests, 'album': api_get_more_to_albums}
V_DICT = {'post': PostView, 'quest': QuestView, 'album': AlbumView}


def set_jobs(contest):
    jobs = []
    if contest.item_type == 'post':
        elem_jobs = E_DICT[contest.item_type].objects.filter(contest=contest)
        for elem_job in elem_jobs:
            jobs.append(elem_job.post)
    elif contest.item_type == 'quest':
        elem_jobs = E_DICT[contest.item_type].objects.filter(contest=contest)
        for elem_job in elem_jobs:
            jobs.append(elem_job.quest)
    elif contest.item_type == 'album':
        elem_jobs = E_DICT[contest.item_type].objects.filter(contest=contest)
        for elem_job in elem_jobs:
            jobs.append(elem_job.album)
    return sorted(jobs, key=operator.attrgetter('date'), reverse=True)

def get_jobs(contest, is_api=False):
    jobs = set_jobs(contest)
    if is_api:
        return API_F_DICT[contest.item_type](S_DICT[contest.item_type](jobs, many=True).data)
    return F_DICT[contest.item_type](jobs)
        
def get_prize(contest):
    print(contest)
    prize = P_DICT[contest['item_type']].objects.filter(contest=contest['id']).first()
    results = {}
    try:
        results['one_place'] = [{'user': prize.one_place.user.username, contest['item_type']: prize.one_place.title, 'slug': prize.one_place.slug}]
        results['two_place'] = [{'user': prize.two_place.user.username, contest['item_type']: prize.two_place.title, 'slug': prize.two_place.slug}]
        results['three_place'] = [{'user': prize.three_place.user.username, contest['item_type']: prize.three_place.title, 'slug': prize.three_place.slug}]
        results['four_place'] = [{'user': prize.four_place.user.username, contest['item_type']: prize.four_place.title, 'slug': prize.four_place.slug}]
        results['five_place'] = [{'user': prize.five_place.user.username, contest['item_type']: prize.five_place.title, 'slug': prize.five_place.slug}]
        results['six_place'] = [{'user': prize.six_place.user.username, contest['item_type']: prize.six_place.title, 'slug': prize.six_place.slug}]
        results['seven_place'] = [{'user': prize.seven_place.user.username, contest['item_type']: prize.seven_place.title, 'slug': prize.seven_place.slug}]
        results['eight_place'] = [{'user': prize.eight_place.user.username, contest['item_type']: prize.eight_place.title, 'slug': prize.eight_place.slug}]
        results['nine_place'] = [{'user': prize.nine_place.user.username, contest['item_type']: prize.nine_place.title, 'slug': prize.nine_place.slug}]
        results['ten_place'] = [{'user': prize.ten_place.user.username, contest['item_type']: prize.ten_place.title, 'slug': prize.ten_place.slug}]
    except AttributeError as e:
        pass
    return results

def func_contests():
    present = timezone.now()
    contests = Contest.objects.filter(is_end=False)
    for contest in contests:
        if contest.end_date <= present:
            if not P_DICT[contest.item_type].objects.filter(contest=contest):
                kwargs = {
                    1: 'one_place',
                    2: 'two_place',
                    3: 'three_place',
                    4: 'four_place',
                    5: 'five_place',
                    6: 'six_place',   
                    7: 'seven_place',  
                    8: 'eight_place',
                    9: 'nine_place',
                    10: 'ten_place',                      
                }
                jobs = set_jobs(contest)
                for job in jobs:
                    filter_kwargs = {contest.item_type: job}
                    if contest.criteries == 'views':
                        job.count_views = V_DICT[contest.item_type].objects.filter(**filter_kwargs).count()
                        sort = 'count_views'
                    elif contest.criteries == 'likes':
                        job.count_likes = L_DICT[contest.item_type].objects.filter(**filter_kwargs).count()
                        sort = 'count_likes'
                jobs = sorted(jobs, key=operator.attrgetter(sort), reverse=True)[:10]
                count = 1
                create_kwargs = {'contest': contest}
                for job in jobs:
                    notificatons_kwargs = {
                        'contest_' + contest.item_type: job, 
                        'user': job.user, 
                        'contest': contest,
                        'text': f'You took {count} place!'
                    }
                    Notification.objects.create(**notificatons_kwargs)
                    create_kwargs[kwargs[count]] = job
                    count += 1
                P_DICT[contest.item_type].objects.create(**create_kwargs)
                