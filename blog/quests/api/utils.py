from comments.models import Comment, Answer

from quests.models import QuestView

from users.models import User


def get_views_and_comments_to_quests(quests):
    for quest in quests:
        count_comments = Comment.objects.filter(quest=quest["id"]).count()
        count_answers = Answer.objects.filter(quest=quest["id"]).count()
        count_comments = count_comments + count_answers
        quest["count_comments"] = count_comments

        quest["count_views"] = QuestView.objects.filter(quest=quest["id"]).count()

        quest["user"] = User.objects.get(id=quest["user"]).username

        quest["namespace"] = "quests"

    return quests