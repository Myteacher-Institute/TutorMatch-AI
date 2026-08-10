from django.contrib.sitemaps import Sitemap
from .models import BlogPost, BlogCategory


class BlogPostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return BlogPost.objects.published()

    def lastmod(self, obj):
        return obj.updated_at


class BlogCategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return BlogCategory.objects.filter(posts__status=BlogPost.STATUS_PUBLISHED).distinct()

    def location(self, obj):
        return obj.get_absolute_url()
