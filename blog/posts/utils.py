from posts.models import Post
from comments.models import Comment, Answer
from posts.models import PostView, PostLike


def popular_blogs():
    posts = Post.objects.all()
    for post in posts:
        post.mouth_scores = 0
        post.save()

def get_more_to_posts(posts):
    for post in posts:
        post.count_views = PostView.objects.filter(post=post).count() 
        post.count_comments = Comment.objects.filter(post=post).count() + Answer.objects.filter(post=post).count()
        post.count_likes = PostLike.objects.filter(post=post).count()
    return posts