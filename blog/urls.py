from rest_framework_nested import routers
from .views import AuthorViewSet, SubscriptionViewSet

router = routers.DefaultRouter()
router.register("authors", AuthorViewSet)
router.register("subscriptions", SubscriptionViewSet)

urlpatterns = router.urls
