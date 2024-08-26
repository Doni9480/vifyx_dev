from comments.models import Comment, Answer
from surveys.models import SurveyView, SurveyLike

                
def get_more_to_surveys(surveys):
    for survey in surveys:
        survey.count_views = SurveyView.objects.filter(survey=survey).count()
        survey.count_comments = Comment.objects.filter(survey=survey).count() + Answer.objects.filter(survey=survey).count()
        survey.count_likes = SurveyLike.objects.filter(survey=survey).count()    
    return surveys