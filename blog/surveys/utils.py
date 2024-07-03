from comments.models import Comment, Answer

from surveys.models import SurveyView

from blogs.models import PaidFollow

                
def get_views_and_comments_to_surveys(surveys):
    for survey in surveys:
        count_comments = Comment.objects.filter(survey=survey).count()
        count_answers = Answer.objects.filter(survey=survey).count()
        survey.count_views = SurveyView.objects.filter(survey=survey).count()
    
        count_comments = count_comments + count_answers
        survey.count_comments = count_comments
        
        survey.namespace = 'surveys'
        
    return surveys

def opening_access(survey, user):
    is_exp = False
    if survey.level_access > 1:
        if user.is_anonymous:
            return True
        paid_follow = PaidFollow.objects.filter(blog=survey.blog, follower=user.id)
        if not (paid_follow and paid_follow[0].blog_access_level.level >= survey.level_access):
            is_exp = True
            
    if (survey.hide_to_moderator or survey.hide_to_user or int(survey.language) != int(user.language)) and not user.is_staff:
        is_exp = True
        
    if survey.user == user:
        is_exp = False
        
    return is_exp