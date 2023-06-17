from rest_framework_nested import routers
from .views import AuthorViewSet

router = routers.DefaultRouter()
router.register("authors", AuthorViewSet)

# URLConf
urlpatterns = router.urls
