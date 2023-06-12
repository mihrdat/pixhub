from rest_framework_nested import routers
from .views import AuthorViewSet, ArticleViewSet

router = routers.DefaultRouter()
router.register("authors", AuthorViewSet)
router.register("articles", ArticleViewSet)

# URLConf
urlpatterns = router.urls
