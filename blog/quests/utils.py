from comments.models import Comment, Answer
from quests.models import QuestView, QuestLike

    
def get_more_to_quests(quests):
    for quest in quests:
        quest.count_views = QuestView.objects.filter(quest=quest).count()
        quest.count_comments = Comment.objects.filter(quest=quest).count() + Answer.objects.filter(quest=quest).count()
        quest.count_likes = QuestLike.objects.filter(quest=quest).count()
    return quests