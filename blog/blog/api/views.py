from rest_framework.decorators import api_view
from rest_framework.response import Response

from posts.models import Post
from posts.api.utils import get_views_and_comments_to_posts

from surveys.models import Survey, SurveyRadio
from surveys.api.utils import get_views_and_comments_to_surveys

from .serializers import PostSerializer, SurveySerializer


# "data": [
#     {
#         "id": 10,
#         "preview": "/media/uploads/image.jpg",
#         "slug": "9242686505-dasdsa",
#         "date": "2024-06-02T19:35:24.277722Z",
#         "user": "admin1",
#         "description": "das",
#         "scores": 7000
#     },
# ]
@api_view(["GET"])
def best_blogs(request):
    if not request.user.is_staff:
        posts = Post.level_access_objects.filter(
            hide_to_user=False, hide_to_moderator=False, language=request.user.language
        )
        surveys = Survey.level_access_objects.filter(
            hide_to_user=False, hide_to_moderator=False, language=request.user.language
        )
    else:
        posts = Post.level_access_objects.filter(language=request.user.language)
        surveys = Survey.level_access_objects.filter(language=request.user.language)

    posts = get_views_and_comments_to_posts(PostSerializer(posts, many=True).data)
    surveys = get_views_and_comments_to_surveys(
        SurveySerializer(surveys, many=True).data
    )

    for survey in surveys:
        survey["scores"] = 0
        options = SurveyRadio.objects.filter(survey=survey["id"])
        for option in options:
            survey["scores"] += option.scores

    blog_list = posts + surveys
    blog_data = sorted(blog_list, key=lambda d: d["scores"], reverse=True)

    return Response({"data": blog_data})
