from django.http import Http404
from custom_tests.models import TestView, TestLike
from comments.models import Comment, Answer


def get_more_to_tests(tests):
    for test in tests:
        test.count_views = TestView.objects.filter(test=test).count()
        test.count_comments = Comment.objects.filter(test=test).count() + Answer.objects.filter(test=test).count()
        test.count_likes = TestLike.objects.filter(test=test).count()
    return tests