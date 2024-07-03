import datetime
import pytz

from blogs.models import PaidFollow


def func_is_valid_comment(request, serializer):
    data = {}

    if request.user.is_published_comment:
        if serializer.is_valid():
            comment = serializer.save()
            comment.user = request.user
            comment.save()

            try:
                tzname = request.data.get("timezone", False)
                date = comment.date.replace(tzinfo=pytz.utc).astimezone(
                    pytz.timezone(tzname)
                )
            except Exception:
                date = comment.date

            data["success"] = "ok."
            data["id"] = comment.id
            data["username"] = comment.user.username
            data["date"] = datetime.datetime.strftime(date, "%d %B %Y %#H:%M")
            data["text"] = comment.text
        else:
            data = serializer.errors
    else:
        data["ban"] = "You can't publish comments."

    return data


def func_is_valid_answer(request, serializer):
    data = {}

    if request.user.is_published_comment:
        if serializer.is_valid():
            answer = serializer.save()
            answer.user = request.user
            answer.save()

            try:
                tzname = request.data.get("timezone", False)
                date = answer.date.replace(tzinfo=pytz.utc).astimezone(
                    pytz.timezone(tzname)
                )
            except Exception:
                date = answer.date

            data["success"] = "ok."
            data["id"] = answer.id
            data["username"] = answer.user.username
            data["date"] = datetime.datetime.strftime(date, "%d %B %Y %#H:%M")
            data["text"] = answer.text
        else:
            data = serializer.errors
    else:
        data["ban"] = "You can't publish comments."

    return data


def opening_access(e, user):
    is_exp = False
    if e.level_access > 1:
        if user.is_anonymous:
            return True
        paid_follow = PaidFollow.objects.filter(blog=e.blog, follower=user.id)
        if not (
            paid_follow and paid_follow[0].blog_access_level.level >= e.level_access
        ):
            is_exp = True

    if (
        e.hide_to_moderator or e.hide_to_user or int(e.language) != int(user.language)
    ) and not user.is_staff:
        is_exp = True

    if e.user == user:
        is_exp = False

    return is_exp
