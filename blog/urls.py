from rest_framework_nested import routers
from .views import AuthorViewSet, ArticleViewSet

router = routers.DefaultRouter()
router.register("authors", AuthorViewSet)

authors_router = routers.NestedDefaultRouter(router, "authors", lookup="author")
authors_router.register("articles", ArticleViewSet, basename="author-articles")

# URLConf
urlpatterns = router.urls + authors_router.urls
