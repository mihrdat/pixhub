from rest_framework_nested import routers
from .views import (
    AuthorViewSet,
    SubscriptionViewSet,
    ArticleViewSet,
    LikeViewSet,
)

router = routers.DefaultRouter()
router.register("authors", AuthorViewSet)
router.register("subscriptions", SubscriptionViewSet)
router.register("articles", ArticleViewSet)

articles_router = routers.NestedDefaultRouter(router, "articles", lookup="article")
articles_router.register("likes", LikeViewSet, basename="article-likes")

# URLConf
urlpatterns = router.urls + articles_router.urls
