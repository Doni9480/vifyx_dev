from comments.models import Comment, Answer
from quests.models import QuestView, QuestLike
from users.models import User


def get_more_to_quests(quests):
    for quest in quests:
        quest["count_comments"] = Comment.objects.filter(quest=quest["id"]).count() + Answer.objects.filter(quest=quest["id"]).count()
        quest["count_views"] = QuestView.objects.filter(quest=quest["id"]).count()
        quest["count_likes"] = QuestLike.objects.filter(quest=quest["id"]).count()
        quest["user"] = User.objects.get(id=quest["user"]).username
        quest["namespace"] = "quests"
    return quests