from comments.models import Comment, Answer
from albums.models import AlbumView, AlbumLike
from users.models import User


def get_more_to_albums(albums):
    for album in albums:
        album["count_comments"] = Comment.objects.filter(album=album["id"]).count() + Answer.objects.filter(album=album["id"]).count()
        album["count_views"] = AlbumView.objects.filter(album=album["id"]).count()
        album["count_likes"] = AlbumLike.objects.filter(album=album["id"]).count()
        album["user"] = User.objects.get(id=album["user"]).username
        album["namespace"] = "albums"
    return albums