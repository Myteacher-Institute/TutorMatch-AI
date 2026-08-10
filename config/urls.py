from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.generic import TemplateView

from tutors.sitemaps import CourseOfferSitemap, StaticViewSitemap, TutorProfileSitemap
from blog.sitemaps import BlogPostSitemap, BlogCategorySitemap

sitemaps = {
    "static": StaticViewSitemap,
    "tutors": TutorProfileSitemap,
    "courses": CourseOfferSitemap,
    "blog": BlogPostSitemap,
    "blog_categories": BlogCategorySitemap,
}

urlpatterns = [
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
        name="robots",
    ),
    path("", include("dashboard.urls")),
    path("", include("accounts.urls")),
    path("", include("tutors.urls")),
    path("", include("ai_search.urls")),
    path("", include("bookings.urls")),
    path("", include("payments.urls")),
    path("", include("reviews.urls")),
    path("", include("blog.urls")),
    path("", include(("Chat.urls", "Chat"), namespace="chat")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
