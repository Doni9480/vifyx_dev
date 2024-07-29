from comments.models import Comment, Answer
from surveys.models import SurveyView
from blogs.models import PaidFollow
from django.http import Http404

                
def get_views_and_comments_to_surveys(surveys):
    for survey in surveys:
        count_comments = Comment.objects.filter(survey=survey).count()
        count_answers = Answer.objects.filter(survey=survey).count()
        survey.count_views = SurveyView.objects.filter(survey=survey).count()
    
        count_comments = count_comments + count_answers
        survey.count_comments = count_comments
        
        survey.namespace = 'surveys'
        
    return surveys