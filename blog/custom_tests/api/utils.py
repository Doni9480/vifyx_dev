from comments.models import Comment, Answer
from custom_tests.models import TestView, TestLike
from users.models import User


def get_more_to_tests(tests):
    for test in tests:
        test["count_comments"] = Comment.objects.filter(test=test["id"]).count() + Answer.objects.filter(test=test["id"]).count()
        test["count_views"] = TestView.objects.filter(test=test["id"]).count()
        test["count_likes"] = TestLike.objects.filter(test=test["id"]).count()
        test["user"] = User.objects.get(id=test["user"]).username
        test["namespace"] = "tests"
    return tests