from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("users.urls")),
]

if settings.DEBUG:
    urlpatterns = [
        path("", include("pixhub.urls.swagger")),
        path("__debug__/", include("debug_toolbar.urls")),
        path("silk/", include("silk.urls", namespace="silk")),
        *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
        *urlpatterns,
    ]
