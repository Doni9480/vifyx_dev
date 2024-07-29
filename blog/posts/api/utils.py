from comments.models import Comment, Answer

from posts.models import PostView

from custom_tests.models import Test

from users.models import User


def get_views_and_comments_to_posts(posts):
    for post in posts:
        count_comments = Comment.objects.filter(post=post["id"]).count()
        count_answers = Answer.objects.filter(post=post["id"]).count()
        count_comments = count_comments + count_answers
        post["count_comments"] = count_comments

        post["count_views"] = PostView.objects.filter(post=post["id"]).count()

        post["user"] = User.objects.get(id=post["user"]).username

        post["namespace"] = "posts"

    return posts

def create_test(post):
    test = Test.objects.create(
        title=post.title,
        user=post.user,
        hidden=True,
        blog=post.blog,
        level_access=post.level_access,
    )
    return test