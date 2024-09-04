from users.models import Token
from users.models import Subcategory_post as Usersubcategory_post
from users.models import Subcategory_survey as Usersubcategory_survey
from users.models import Subcategory_test as Usersubcategory_test
from users.models import Subcategory_quest as Usersubcategory_quest
from users.models import Subcategory_album as Usersubcategory_album
from posts.models import Category as Category_post, Subcategory as Subcategory_post
from surveys.models import Category as Category_survey, Subcategory as Subcategory_survey
from custom_tests.models import Category as Category_test, Subcategory as Subcategory_test
from quests.models import Category as Category_quest, Subcategory as Subcategory_quest
from albums.models import Category as Category_album, Subcategory as Subcategory_album


N_DICT = {
    'posts': {'model': Category_post, 'user_subcategory': Usersubcategory_post, 'user_category': 'posts_category', 'subcategory': Subcategory_post},
    'surveys': {'model': Category_survey, 'user_subcategory': Usersubcategory_survey, 'user_category': 'surveys_category', 'subcategory': Subcategory_survey},
    'quests': {'model': Category_quest, 'user_subcategory': Usersubcategory_quest, 'user_category': 'quests_category', 'subcategory': Subcategory_quest},
    'tests': {'model': Category_test, 'user_subcategory': Usersubcategory_test, 'user_category': 'tests_category', 'subcategory': Subcategory_test},
    'albums': {'model': Category_album, 'user_subcategory': Usersubcategory_album, 'user_category': 'albums_category', 'subcategory': Subcategory_album},
}

def delete_token(user):
    user_token = Token.objects.filter(user_id=user)
    if user_token:
        user_token.first()
        user_token.delete()
