from comments.models import Comment, Answer

from albums.models import AlbumView

from users.models import User


def get_views_and_comments_to_albums(albums):
    for album in albums:
        count_comments = Comment.objects.filter(album=album["id"]).count()
        count_answers = Answer.objects.filter(album=album["id"]).count()
        count_comments = count_comments + count_answers
        album["count_comments"] = count_comments

        album["count_views"] = AlbumView.objects.filter(album=album["id"]).count()

        album["user"] = User.objects.get(id=album["user"]).username

        album["namespace"] = "albums"

    return albums