from comments.models import Comment, Answer

from posts.models import PostView

from users.models import User


def get_views_and_comments_to_posts(posts):
    for post in posts:
        count_comments = Comment.objects.filter(post=post["id"]).count()
        count_answers = Answer.objects.filter(post=post["id"]).count()
        count_comments = count_comments + count_answers
        post["count_comments"] = count_comments

        post["count_surveys"] = PostView.objects.filter(post=post["id"]).count()

        post["user"] = User.objects.get(id=post["user"]).username

        post["namespace"] = "posts"

    return posts
