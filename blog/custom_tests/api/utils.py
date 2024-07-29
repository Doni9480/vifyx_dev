from comments.models import Comment, Answer

from custom_tests.models import TestView

from users.models import User


def get_views_and_comments_to_tests(tests):
    for test in tests:
        count_comments = Comment.objects.filter(test=test["id"]).count()
        count_answers = Answer.objects.filter(test=test["id"]).count()
        count_comments = count_comments + count_answers
        test["count_comments"] = count_comments

        test["count_views"] = TestView.objects.filter(test=test["id"]).count()

        test["user"] = User.objects.get(id=test["user"]).username

        test["namespace"] = "tests"

    return tests