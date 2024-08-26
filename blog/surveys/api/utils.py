from comments.models import Comment, Answer
from surveys.models import SurveyView, SurveyLike
from users.models import User


def get_more_to_surveys(surveys):
    for survey in surveys:
        survey["count_comments"] = Comment.objects.filter(survey=survey["id"]).count() + Answer.objects.filter(survey=survey["id"]).count()
        survey["count_views"] = SurveyView.objects.filter(survey=survey["id"]).count()
        survey["count_likes"] = SurveyLike.objects.filter(survey=survey["id"]).count()
        survey["user"] = User.objects.get(id=survey["user"]).username
        survey["namespace"] = "surveys"
    return surveys