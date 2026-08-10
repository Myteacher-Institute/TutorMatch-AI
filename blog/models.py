import math
import re
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import F
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class BlogCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, db_index=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=60, default="fa-newspaper", help_text="FontAwesome icon class, e.g. fa-graduation-cap")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Blog Category"
        verbose_name_plural = "Blog Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog_category_list", kwargs={"slug": self.slug})

    @property
    def published_post_count(self):
        return self.posts.filter(status=BlogPost.STATUS_PUBLISHED).count()


class BlogPostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(
            status=BlogPost.STATUS_PUBLISHED,
            published_at__lte=timezone.now()
        )

    def featured(self):
        return self.published().filter(is_featured=True)


class BlogPost(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_ARCHIVED = "archived"

    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_PUBLISHED, "Published"),
        (STATUS_ARCHIVED, "Archived"),
    ]

    title = models.CharField(max_length=255, help_text="Engaging, SEO-rich headline")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, blank=True, help_text="URL-friendly slug (auto-generated if empty)")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="blog_posts")
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="posts")
    
    # Media & Display
    image = models.ImageField(upload_to="blog_images/%Y/%m/", blank=True, null=True, help_text="Upload article featured banner image")
    image_url = models.URLField(max_length=500, blank=True, help_text="Or external image URL / CDN link")
    
    # Content
    excerpt = models.TextField(max_length=500, help_text="Summary shown on listing cards and used as default search snippet")
    content = models.TextField(help_text="Full post content (supports HTML / formatted text)")
    
    # SEO On-Page Optimization
    meta_title = models.CharField(max_length=150, blank=True, help_text="Custom SEO page title (defaults to post title)")
    meta_description = models.CharField(max_length=300, blank=True, help_text="Custom SEO meta description (defaults to excerpt)")
    meta_keywords = models.CharField(max_length=300, blank=True, help_text="Comma-separated SEO keywords (e.g. waec tutors, math lesson lagos)")
    
    # Settings & Metrics
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PUBLISHED)
    is_featured = models.BooleanField(default=False, help_text="Pin as a featured hero article on the blog home")
    views_count = models.PositiveIntegerField(default=0)
    estimated_read_time = models.PositiveSmallIntegerField(default=3, help_text="Estimated read time in minutes")
    
    # Timestamps
    published_at = models.DateTimeField(default=timezone.now, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = BlogPostQuerySet.as_manager()

    class Meta:
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"
        ordering = ["-is_featured", "-published_at", "-created_at"]

    def __str__(self):
        return self.title

    def _generate_unique_slug(self):
        base_slug = slugify(self.title) or "article"
        slug = base_slug
        counter = 1
        qs = BlogPost.objects.all()
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        while qs.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug

    def _calculate_read_time(self):
        # Average reading speed: 200 words per minute
        clean_text = re.sub(r"<[^>]+>", " ", self.content or "")
        words = len(clean_text.split())
        return max(1, math.ceil(words / 200))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        if not self.estimated_read_time or self.estimated_read_time <= 0:
            self.estimated_read_time = self._calculate_read_time()
        if self.status == self.STATUS_PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog_detail", kwargs={"slug": self.slug})

    @property
    def effective_image_url(self):
        if self.image:
            try:
                return self.image.url
            except Exception:
                pass
        if self.image_url:
            if self.image_url.startswith("/") or self.image_url.startswith("http"):
                return self.image_url
            return f"/static/{self.image_url}"
        return "/static/images/blog/african-students-study-group.png"

    def get_meta_title(self):
        return self.meta_title.strip() if self.meta_title else f"{self.title} | MyteacherConnect Blog"

    def get_meta_description(self):
        if self.meta_description:
            return self.meta_description.strip()
        if self.excerpt:
            return self.excerpt.strip()
        # Strip HTML and truncate content
        clean = re.sub(r"<[^>]+>", " ", self.content or "").strip()
        return clean[:160] + "..." if len(clean) > 160 else clean

    def get_meta_keywords(self):
        if self.meta_keywords:
            return self.meta_keywords.strip()
        category_name = self.category.name if self.category else "education"
        return f"{self.title}, {category_name}, home tutors nigeria, private tutor lagos, port harcourt tutor, MyteacherConnect"

    @property
    def author_display_name(self):
        if not self.author:
            return "Admin"
        full_name = self.author.get_full_name().strip()
        if not full_name or "marketplace" in full_name.lower() or full_name.lower() in ["admin", "administrator", "staff"]:
            return "Admin"
        if self.author.is_staff or self.author.is_superuser:
            return "Admin"
        return full_name

    def increment_views(self):
        BlogPost.objects.filter(pk=self.pk).update(views_count=F("views_count") + 1)
        self.views_count += 1
