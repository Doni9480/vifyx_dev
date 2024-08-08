from posts.models import Post, PostDayView, PostWeekView
from posts.api.serializers import PostShowSerializer
from posts.api.utils import get_views_and_comments_to_posts
from surveys.models import Survey, SurveyDayView, SurveyWeekView
from surveys.api.serializers import SurveyShowSerializer
from surveys.api.utils import get_views_and_comments_to_surveys
from custom_tests.models import Test, TestDayView, TestWeekView
from custom_tests.api.utils import get_views_and_comments_to_tests
from custom_tests.api.serializers import TestSerializer
from quests.models import Quest, QuestDayView, QuestWeekView
from quests.api.serializers import QuestSerializer
from quests.api.utils import get_views_and_comments_to_quests
from users.models import User
from blogs.api.serializers import PopularUserSerializer


def get_blog_list(filter_kwargs):
    posts = get_views_and_comments_to_posts(
        PostShowSerializer(Post.level_access_objects.filter(**filter_kwargs), many=True).data
    )
    surveys = get_views_and_comments_to_surveys(
        SurveyShowSerializer(Survey.level_access_objects.filter(**filter_kwargs), many=True).data
    )
    tests = get_views_and_comments_to_tests(
        TestSerializer(Test.level_access_objects.filter(**filter_kwargs), many=True).data
    )
    quests = get_views_and_comments_to_quests(
        QuestSerializer(Quest.level_access_objects.filter(**filter_kwargs), many=True).data
    )
    blog_list = posts + surveys + tests + quests
    return blog_list

E_DICTS = [
    {
        'obj': 'post', 
        'model': Post, 
        'view_day': PostDayView, 
        'view_week': PostWeekView, 
        'serializer': PostShowSerializer,
        'func': get_views_and_comments_to_posts
    }, 
    {
        'obj': 'survey', 
        'model': Survey, 
        'view_day': SurveyDayView, 
        'view_week': SurveyWeekView, 
        'serializer': SurveyShowSerializer,
        'func': get_views_and_comments_to_surveys
    },
    {
        'obj': 'quest', 
        'model': Quest, 
        'view_day': QuestDayView, 
        'view_week': QuestWeekView, 
        'serializer': QuestSerializer,
        'func': get_views_and_comments_to_quests
    },
    {
        'obj': 'test', 
        'model': Test, 
        'view_day': TestDayView, 
        'view_week': TestWeekView, 
        'serializer': TestSerializer,
        'func': get_views_and_comments_to_tests
    }
]

def get_views_period(filter_kwargs, full=False):
    popular = []
    for e_dict in E_DICTS:
        elements = e_dict['func'](e_dict['serializer'](e_dict['model'].level_access_objects.filter(**filter_kwargs), many=True).data)
        for element in elements:
            filter_model = {e_dict['obj']: element['id']}
            element['views_day'] = e_dict['view_day'].objects.filter(**filter_model).count()
            element['views_week'] = e_dict['view_week'].objects.filter(**filter_model).count()
            popular.append(element)

    if full:
        return (
            sorted(popular, key=lambda d: d['views_day'], reverse=True),
            sorted(popular, key=lambda d: d['views_week'], reverse=True),
        )
    return (
        sorted(popular, key=lambda d: d['views_day'], reverse=True)[:3],
        sorted(popular, key=lambda d: d['views_week'], reverse=True)[:3],
    )
    
def get_users_period(full=False):
    users = PopularUserSerializer(User.objects.all(), many=True).data
    for user in users:
        user['views_day'] = 0
        user['views_week'] = 0
    for e_dict in E_DICTS:
        for user in users:
            elements = e_dict['model'].objects.filter(user=user['id'])
            for element in elements:
                filter_model = {e_dict['obj']: element}
                user['views_day'] += e_dict['view_day'].objects.filter(**filter_model).count()
                user['views_week'] += e_dict['view_week'].objects.filter(**filter_model).count()
            
    if full:
        return (
            sorted(users, key=lambda d: d['views_day'], reverse=True),
            sorted(users, key=lambda d: d['views_week'], reverse=True),
        )
    return (
        sorted(users, key=lambda d: d['views_day'], reverse=True)[:3],
        sorted(users, key=lambda d: d['views_week'], reverse=True)[:3],
    )
    