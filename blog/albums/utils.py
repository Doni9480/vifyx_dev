from albums.models import Album
from comments.models import Comment, Answer
from albums.models import AlbumView


def get_views_and_comments_to_albums(albums):
    for album in albums:
        count_comments = Comment.objects.filter(album=album).count()
        count_answers = Answer.objects.filter(album=album).count()
        album.count_views = AlbumView.objects.filter(album=album).count()
    
        count_comments = count_comments + count_answers
        album.count_comments = count_comments
        
        album.namespace = 'albums'
        
    return albums