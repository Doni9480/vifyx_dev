from django.http import Http404
from custom_tests.models import TestView
from comments.models import Comment, Answer


def get_views_and_comments_to_tests(tests):
    for test in tests:
        count_comments = Comment.objects.filter(test=test).count()
        count_answers = Answer.objects.filter(test=test).count()
        test.count_views = TestView.objects.filter(test=test).count()
    
        count_comments = count_comments + count_answers
        test.count_comments = count_comments
        
        test.namespace = 'tests'
        
    return tests