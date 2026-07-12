from config import settings as project_settings
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("dashboard.urls")),
    path("", include("accounts.urls")),
    path("", include("tutors.urls")),
    path("", include("ai_search.urls")),
    path("", include("bookings.urls")),
    path("", include("payments.urls")),
    path("", include("reviews.urls")),
    path("", include(("Chat.urls", "Chat"), namespace="chat")),
]

if getattr(project_settings.Django_middleware, "securitys", ""):
    urlpatterns.append(path(f"{project_settings.Django_middleware.securitys}/", admin.site.urls))

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
