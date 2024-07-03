from comments.models import Comment, Answer

from surveys.models import SurveyView

from users.models import User


def get_views_and_comments_to_surveys(surveys):
    for survey in surveys:
        count_comments = Comment.objects.filter(survey=survey["id"]).count()
        count_answers = Answer.objects.filter(survey=survey["id"]).count()
        count_comments = count_comments + count_answers
        survey["count_comments"] = count_comments

        survey["count_views"] = SurveyView.objects.filter(survey=survey["id"]).count()

        survey["user"] = User.objects.get(id=survey["user"]).username

        survey["namespace"] = "surveys"

    return surveys
