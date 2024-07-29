from posts.models import Post
from comments.models import Comment, Answer
from posts.models import PostView

def popular_blogs():
    posts = Post.objects.all()
    for post in posts:
        post.mouth_scores = 0
        post.save()

def get_views_and_comments_to_posts(posts):
    for post in posts:
        count_comments = Comment.objects.filter(post=post).count()
        count_answers = Answer.objects.filter(post=post).count()
        post.count_views = PostView.objects.filter(post=post).count()
    
        count_comments = count_comments + count_answers
        post.count_comments = count_comments
        
        post.namespace = 'posts'
        
    return posts