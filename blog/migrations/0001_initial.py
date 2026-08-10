# Generated for Blog App
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="BlogCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True)),
                ("slug", models.SlugField(max_length=120, unique=True)),
                ("description", models.TextField(blank=True)),
                ("icon", models.CharField(default="fa-newspaper", help_text="FontAwesome icon class, e.g. fa-graduation-cap", max_length=60)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Blog Category",
                "verbose_name_plural": "Blog Categories",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="BlogPost",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(help_text="Engaging, SEO-rich headline", max_length=255)),
                ("slug", models.SlugField(blank=True, help_text="URL-friendly slug (auto-generated if empty)", max_length=255, unique=True)),
                ("image", models.ImageField(blank=True, help_text="Upload article featured banner image", null=True, upload_to="blog_images/%Y/%m/")),
                ("image_url", models.URLField(blank=True, help_text="Or external image URL / CDN link", max_length=500)),
                ("excerpt", models.TextField(help_text="Summary shown on listing cards and used as default search snippet", max_length=500)),
                ("content", models.TextField(help_text="Full post content (supports HTML / formatted text)")),
                ("meta_title", models.CharField(blank=True, help_text="Custom SEO page title (defaults to post title)", max_length=150)),
                ("meta_description", models.CharField(blank=True, help_text="Custom SEO meta description (defaults to excerpt)", max_length=300)),
                ("meta_keywords", models.CharField(blank=True, help_text="Comma-separated SEO keywords (e.g. waec tutors, math lesson lagos)", max_length=300)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("published", "Published"), ("archived", "Archived")], default="published", max_length=20)),
                ("is_featured", models.BooleanField(default=False, help_text="Pin as a featured hero article on the blog home")),
                ("views_count", models.PositiveIntegerField(default=0)),
                ("estimated_read_time", models.PositiveSmallIntegerField(default=3, help_text="Estimated read time in minutes")),
                ("published_at", models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("author", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="blog_posts", to=settings.AUTH_USER_MODEL)),
                ("category", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="posts", to="blog.blogcategory")),
            ],
            options={
                "verbose_name": "Blog Post",
                "verbose_name_plural": "Blog Posts",
                "ordering": ["-is_featured", "-published_at", "-created_at"],
            },
        ),
    ]
