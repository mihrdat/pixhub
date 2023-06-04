from rest_framework_nested import routers
from .views import AuthorViewSet, SubscriptionViewSet, ArticleViewSet

router = routers.DefaultRouter()
router.register("authors", AuthorViewSet)
router.register("subscriptions", SubscriptionViewSet)

authors_router = routers.NestedDefaultRouter(router, "authors", lookup="author")
authors_router.register("articles", ArticleViewSet, basename="author-articles")

# URLConf
urlpatterns = router.urls + authors_router.urls
