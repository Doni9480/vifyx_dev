from comments.models import Comment, Answer
from posts.models import PostView, PostLike
from custom_tests.models import Test
from users.models import User


def get_more_to_posts(posts):
    for post in posts:
        post["count_comments"] = Comment.objects.filter(post=post["id"]).count() + Answer.objects.filter(post=post["id"]).count()
        post["count_views"] = PostView.objects.filter(post=post["id"]).count()
        post["count_likes"] = PostLike.objects.filter(post=post["id"]).count()
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