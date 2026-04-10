from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from accounts.views import notifications_api

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("services.web_urls")),
    path("accounts/", include("accounts.web_urls")),
    path("bookings/", include("bookings.web_urls")),
    path("api/", include("api.urls")),
    path("notifications/", notifications_api, name="notifications"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

