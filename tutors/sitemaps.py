from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Tutor, CourseOffer


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "daily"

    def items(self):
        return ["home", "tutor_list", "course_list", "about", "contact", "terms_of_service", "privacy_policy"]

    def location(self, item):
        return reverse(item)


class TutorProfileSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Tutor.objects.filter(is_publicly_visible=True)

    def lastmod(self, obj):
        # Return object last update if available
        return None


class CourseOfferSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.85

    def items(self):
        return CourseOffer.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at
