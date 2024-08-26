from comments.models import Comment, Answer
from albums.models import AlbumView, AlbumLike


def get_more_to_albums(albums):
    for album in albums:
        album.count_views = AlbumView.objects.filter(album=album).count()
        album.count_likes = AlbumLike.objects.filter(album=album).count()
        album.count_comments = Comment.objects.filter(album=album).count() + Answer.objects.filter(album=album).count()
    return albums