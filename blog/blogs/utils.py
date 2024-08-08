from django.utils import timezone
from django.db import transaction
from django.shortcuts import get_object_or_404

from blog.utils import add_months
from blogs.models import PaidFollow
from users.models import User, Percent, Hide
from posts.models import (
    Post, 
    Category as Category_post, 
    Subcategory as Subcategory_post,
    PostDayView,
    PostWeekView
)
from posts.utils import get_views_and_comments_to_posts
from surveys.models import (
    Survey, 
    Category as Category_survey, 
    Subcategory as Subcategory_survey,
    SurveyDayView,
    SurveyWeekView
)
from surveys.utils import get_views_and_comments_to_surveys
from custom_tests.models import (
    Test, 
    Category as Category_test, 
    Subcategory as Subcategory_test,
    TestWeekView,
    TestDayView
)
from custom_tests.utils import get_views_and_comments_to_tests
from quests.models import (
    Quest, 
    Category as Category_quest, 
    Subcategory as Subcategory_quest,
    QuestDayView,
    QuestWeekView
)
from quests.utils import get_views_and_comments_to_quests
from itertools import chain
from operator import attrgetter


@transaction.atomic
def paid_follows():
    present = timezone.now()
    paid_follows = PaidFollow.objects.all()
    for paid_follow in paid_follows:
        if paid_follow.date <= present:
            user = paid_follow.blog.user
            if user.is_autorenewal:
                blog = paid_follow.blog
                price = paid_follow.count_months * paid_follow.blog_access_level.scores
                follower = paid_follow.follower
                follower.scores -= price

                if follower.scores < 0:
                    paid_follow.delete()
                else:
                    follower.save()

                    admin = User.objects.filter(is_superuser=True)[0]
                    percent = Percent.objects.all()[0].percent / 100
                    admin.scores += int(price * percent) or 1
                    admin.save()

                    reverse_percent = 1 - percent
                    blog.user.scores = int(price * reverse_percent) or 1
                    blog.user.save()

                    paid_follow.date = add_months(
                        paid_follow.date, paid_follow.count_months
                    )
                    paid_follow.save()
            else:
                paid_follow.delete()
                
def views_period_day():
    views = [TestDayView, QuestDayView, PostDayView, SurveyDayView]
    for view in views:
        view.objects.all().delete()

def views_period_week():
    views = [TestWeekView, QuestWeekView, PostWeekView, SurveyWeekView]
    for view in views:
        view.objects.all().delete()

def get_filter_kwargs(request):
    filter_kwargs = {'hide_to_user': False, 'hide_to_moderator': False, 'language': request.user.language}
    if request.user.language == 'any':
        del filter_kwargs['language']
    if request.user.is_staff:
        del filter_kwargs['hide_to_moderator']
        del filter_kwargs['hide_to_user']
        
    return filter_kwargs

def get_blog_list(filter_kwargs):
    posts = get_views_and_comments_to_posts(Post.level_access_objects.filter(**filter_kwargs))
    surveys = get_views_and_comments_to_surveys(Survey.level_access_objects.filter(**filter_kwargs))
    tests = get_views_and_comments_to_tests(Test.level_access_objects.filter(**filter_kwargs))
    quests = get_views_and_comments_to_quests(Quest.level_access_objects.filter(**filter_kwargs))
    blog_list = sorted(chain(posts, surveys, tests, quests), key=attrgetter("date"), reverse=True)
    return blog_list

def get_obj_set(obj_set, user):
    hides = Hide.objects.filter(hider=user.id)
    
    obj_set_dict = {}
    for obj in obj_set:
        obj_set_dict[obj.id] = obj
    
    for obj_dict in list(obj_set_dict):
        for hide in hides:
            if hide.user == obj_set_dict[obj_dict].user:
                del obj_set_dict[obj_dict]
                break
                
    obj_set = []
    for obj_dict in list(obj_set_dict):
        obj_set.append(obj_set_dict[obj_dict])
    return obj_set    
    
def get_category(filter_kwargs, request, namespace):
    dict_categories = {
        'posts': [Category_post, Subcategory_post],
        'surveys': [Category_survey, Subcategory_survey],
        'tests': [Category_test, Subcategory_test],
        'quests': [Category_quest, Subcategory_quest],
    }
    
    subcategories = []
    category_q = request.GET.get('category')
    subcategory_q = request.GET.get("subcategory")
    if category_q:
        try:
            category_q = int(category_q)
            category = get_object_or_404(dict_categories[namespace][0], id=category_q)
            filter_kwargs['category'] = category
            
            if subcategory_q:
                subcategory_q = int(subcategory_q) if subcategory_q is not None else None
                subcategory = get_object_or_404(dict_categories[namespace][1], id=subcategory_q)
                filter_kwargs['subcategory'] = subcategory
                
            subcategories = dict_categories[namespace][1].objects.filter(category=category)
        except ValueError:
            subcategories = []
        
    return filter_kwargs, subcategories

E_DICTS = [
        {
            'obj': 'post', 
            'model': Post, 
            'view_day': PostDayView, 
            'view_week': PostWeekView,
            'func': get_views_and_comments_to_posts
        }, 
        {
            'obj': 'survey', 
            'model': Survey, 
            'view_day': SurveyDayView, 
            'view_week': SurveyWeekView,
            'func': get_views_and_comments_to_surveys
        },
        {
            'obj': 'quest', 
            'model': Quest, 
            'view_day': QuestDayView, 
            'view_week': QuestWeekView,
            'func': get_views_and_comments_to_quests
        },
        {
            'obj': 'test', 
            'model': Test, 
            'view_day': TestDayView, 
            'view_week': TestWeekView,
            'func': get_views_and_comments_to_tests
        }
    ]

def get_views_period(filter_kwargs, full=False):
    popular = []
    for e_dict in E_DICTS:
        elements = e_dict['func'](e_dict['model'].level_access_objects.filter(**filter_kwargs))
        for element in elements:
            filter_model = {e_dict['obj']: element}
            element.views_day = e_dict['view_day'].objects.filter(**filter_model).count()
            element.views_week = e_dict['view_week'].objects.filter(**filter_model).count()
        popular.append(elements)
        
    if full:
        return (
            sorted(chain(*popular), key=attrgetter("views_day"), reverse=True), 
            sorted(chain(*popular), key=attrgetter("views_week"), reverse=True),
        )
    return (
        sorted(chain(*popular), key=attrgetter("views_day"), reverse=True)[:3], 
        sorted(chain(*popular), key=attrgetter("views_week"), reverse=True)[:3]
    )
    
def get_users_period(full=False):
    users = User.objects.all()
    for user in users:
        user.views_day = 0
        user.views_week = 0
    for e_dict in E_DICTS:
        for user in users:
            elements = e_dict['model'].objects.filter(user=user)
            for element in elements:
                filter_model = {e_dict['obj']: element}
                user.views_day += e_dict['view_day'].objects.filter(**filter_model).count()
                user.views_week += e_dict['view_week'].objects.filter(**filter_model).count()
            
    if full:
        return (
            sorted(chain(users), key=attrgetter("views_day"), reverse=True), 
            sorted(chain(users), key=attrgetter("views_week"), reverse=True),
        )
    return (
        sorted(chain(users), key=attrgetter("views_day"), reverse=True)[:3], 
        sorted(chain(users), key=attrgetter("views_week"), reverse=True)[:3]
    )