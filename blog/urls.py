from rest_framework_nested import routers
from .views import AuthorViewSet, ArticleViewSet, SubscriberViewSet, SubscriptionViewSet

router = routers.DefaultRouter()
router.register("authors", AuthorViewSet)
router.register("articles", ArticleViewSet)

authors_router = routers.NestedDefaultRouter(router, "authors", lookup="author")
authors_router.register("subscribers", SubscriberViewSet, basename="author-subscribers",)
authors_router.register("subscriptions", SubscriptionViewSet, basename="author-subscriptions")

# URLConf
urlpatterns = router.urls + authors_router.urls
