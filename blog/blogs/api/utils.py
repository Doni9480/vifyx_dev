from posts.models import Post
from posts.api.serializers import PostShowSerializer
from posts.api.utils import get_views_and_comments_to_posts
from surveys.models import Survey
from surveys.api.serializers import SurveyShowSerializer
from surveys.api.utils import get_views_and_comments_to_surveys
from custom_tests.models import Test
from custom_tests.api.utils import get_views_and_comments_to_tests
from custom_tests.api.serializers import TestSerializer
from quests.models import Quest
from quests.api.serializers import QuestSerializer
from quests.api.utils import get_views_and_comments_to_quests


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