from rest_framework_nested import routers
from .views import ChatPageViewSet

router = routers.DefaultRouter()
router.register("pages", ChatPageViewSet)

# URLConf
urlpatterns = router.urls
