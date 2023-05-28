from rest_framework_nested import routers
from .views import AuthorViewSet, SubscriptionViewSet, ArticleViewSet

router = routers.DefaultRouter()
router.register("authors", AuthorViewSet)
router.register("subscriptions", SubscriptionViewSet)
router.register("articles", ArticleViewSet)

urlpatterns = router.urls
