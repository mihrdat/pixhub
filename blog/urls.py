from rest_framework_nested import routers
from .views import AuthorViewSet, RelationViewSet, ArticleViewSet

router = routers.DefaultRouter()
router.register("authors", AuthorViewSet)
router.register("relations", RelationViewSet)

authors_router = routers.NestedDefaultRouter(router, "authors", lookup="author")
authors_router.register("articles", ArticleViewSet, basename="author-articles")

# URLConf
urlpatterns = router.urls + authors_router.urls
