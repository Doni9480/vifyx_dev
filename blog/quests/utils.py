from django.http import Http404
from comments.models import Comment, Answer
from quests.models import QuestView
from blogs.models import PaidFollow

    
def get_views_and_comments_to_quests(quests):
    for quest in quests:
        count_comments = Comment.objects.filter(quest=quest).count()
        count_answers = Answer.objects.filter(quest=quest).count()
        quest.count_views = QuestView.objects.filter(quest=quest).count()
    
        count_comments = count_comments + count_answers
        quest.count_comments = count_comments
        
        quest.namespace = 'quests'
        
    return quests