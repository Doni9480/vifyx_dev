from posts.models import Post

from comments.models import Comment, Answer

from posts.models import PostView

from blogs.models import PaidFollow


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

def opening_access(post, user):
    is_exp = False
    if post.level_access > 1:
        if user.is_anonymous:
            return True
        paid_follow = PaidFollow.objects.filter(blog=post.blog, follower=user.id)
        if not (paid_follow and paid_follow[0].blog_access_level.level >= post.level_access):
            is_exp = True
            
    if (post.hide_to_moderator or post.hide_to_user or int(post.language) != int(user.language)) and not user.is_staff:
        is_exp = True
        
    if post.user == user:
        is_exp = False
        
    return is_exp
