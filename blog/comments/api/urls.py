from .views import CommentViewSet, AnswerViewSet

from blog.routers import CustomRouter

router = CustomRouter()
router.register(r"", CommentViewSet, basename="comment")
router.register(r"answer", AnswerViewSet, basename="comment_answer")

urlpatterns = router.urls
