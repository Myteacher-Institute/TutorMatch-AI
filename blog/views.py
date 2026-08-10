import urllib.parse
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.decorators import admin_required
from .forms import BlogPostForm, BlogCategoryForm
from .models import BlogPost, BlogCategory


# ==========================================
# PUBLIC BLOG VIEWS (SEO & Readers)
# ==========================================

def blog_list(request):
    """
    Public blog directory featuring search, category pills, featured hero post,
    paginated posts grid, and popular articles sidebar.
    """
    search_query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()

    base_qs = BlogPost.objects.published().select_related("author", "category")

    if search_query:
        base_qs = base_qs.filter(
            Q(title__icontains=search_query) |
            Q(excerpt__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(meta_keywords__icontains=search_query)
        )

    current_category = None
    if category_slug:
        current_category = get_object_or_404(BlogCategory, slug=category_slug)
        base_qs = base_qs.filter(category=current_category)

    # Hero featured post (top featured or most recent if no search/category active)
    featured_post = None
    if not search_query and not category_slug:
        featured_post = base_qs.filter(is_featured=True).first()
        if not featured_post:
            featured_post = base_qs.first()
        if featured_post:
            base_qs = base_qs.exclude(pk=featured_post.pk)

    # Pagination
    paginator = Paginator(base_qs, 6)
    page_number = request.GET.get("page", 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    # Categories with post counts
    categories = BlogCategory.objects.annotate(
        published_count=Count("posts", filter=Q(posts__status=BlogPost.STATUS_PUBLISHED))
    ).filter(published_count__gt=0).order_by("-published_count")

    # Popular posts sidebar
    popular_posts = BlogPost.objects.published().order_by("-views_count", "-published_at")[:4]

    context = {
        "posts": posts,
        "featured_post": featured_post,
        "categories": categories,
        "popular_posts": popular_posts,
        "search_query": search_query,
        "current_category": current_category,
        "total_posts_count": BlogPost.objects.published().count(),
    }
    return render(request, "blog/blog_list.html", context)


def blog_category_list(request, slug):
    """Convenience URL for /blog/category/<slug>/ which reuses blog_list logic."""
    category = get_object_or_404(BlogCategory, slug=slug)
    # Redirect or render with category filter
    return blog_list(request)


def blog_detail(request, slug):
    """
    Public article detail page with full content, author bio, social share links,
    related posts, conversion CTA, and schema.org JSON-LD.
    """
    user = request.user
    is_admin = user.is_authenticated and (user.is_staff or user.is_superuser or getattr(getattr(user, "profile", None), "role", "") == "admin")

    # Admins can preview draft posts; public visitors only see published posts
    if is_admin:
        post = get_object_or_404(BlogPost.objects.select_related("author", "category"), slug=slug)
    else:
        post = get_object_or_404(BlogPost.objects.published().select_related("author", "category"), slug=slug)
        # Increment views for public visitors (skip for admin previews)
        post.increment_views()

    # Related articles
    related_posts = BlogPost.objects.published().exclude(pk=post.pk)
    if post.category:
        related_posts = related_posts.filter(category=post.category)
    related_posts = related_posts.order_by("-published_at")[:3]
    if not related_posts.exists():
        related_posts = BlogPost.objects.published().exclude(pk=post.pk).order_by("-published_at")[:3]

    # Pre-computed Social Share URLs
    absolute_url = request.build_absolute_uri(post.get_absolute_url())
    encoded_url = urllib.parse.quote(absolute_url)
    encoded_title = urllib.parse.quote(post.title)
    whatsapp_text = urllib.parse.quote(f"{post.title}\n\nRead more at: {absolute_url}")

    share_urls = {
        "whatsapp": f"https://api.whatsapp.com/send?text={whatsapp_text}",
        "twitter": f"https://twitter.com/intent/tweet?text={encoded_title}&url={encoded_url}&via=MyteacherConn",
        "facebook": f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}",
        "linkedin": f"https://www.linkedin.com/sharing/share-offsite/?url={encoded_url}",
    }

    # Categories for sidebar
    categories = BlogCategory.objects.annotate(
        published_count=Count("posts", filter=Q(posts__status=BlogPost.STATUS_PUBLISHED))
    ).filter(published_count__gt=0).order_by("-published_count")[:6]

    context = {
        "post": post,
        "related_posts": related_posts,
        "share_urls": share_urls,
        "categories": categories,
        "absolute_url": absolute_url,
        "is_admin_preview": is_admin and post.status != BlogPost.STATUS_PUBLISHED,
    }
    return render(request, "blog/blog_detail.html", context)


# ==========================================
# ADMIN BLOG MANAGEMENT VIEWS (@admin_required)
# ==========================================

@admin_required
def admin_blog_list(request):
    """Admin dashboard for managing, searching, and filtering all blog posts."""
    search_query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "").strip()
    category_id = request.GET.get("category", "").strip()

    qs = BlogPost.objects.select_related("author", "category").order_by("-created_at")

    if search_query:
        qs = qs.filter(
            Q(title__icontains=search_query) |
            Q(excerpt__icontains=search_query) |
            Q(slug__icontains=search_query)
        )

    if status_filter:
        qs = qs.filter(status=status_filter)

    if category_id:
        qs = qs.filter(category_id=category_id)

    # Metrics
    all_posts = BlogPost.objects.all()
    stats = {
        "total": all_posts.count(),
        "published": all_posts.filter(status=BlogPost.STATUS_PUBLISHED).count(),
        "drafts": all_posts.filter(status=BlogPost.STATUS_DRAFT).count(),
        "total_views": all_posts.aggregate(total=Sum("views_count"))["total"] or 0,
    }

    # Pagination
    paginator = Paginator(qs, 15)
    page_number = request.GET.get("page", 1)
    posts = paginator.get_page(page_number)

    categories = BlogCategory.objects.all().order_by("name")

    context = {
        "posts": posts,
        "stats": stats,
        "categories": categories,
        "search_query": search_query,
        "status_filter": status_filter,
        "category_id": category_id,
    }
    return render(request, "dashboard/admin_blogs.html", context)


@admin_required
def admin_blog_create(request):
    """Admin page to write a new blog post."""
    if request.method == "POST":
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, f'Blog post "{post.title}" was created successfully!')
            return redirect("admin_blog_list")
        else:
            messages.error(request, "Please correct the errors in the form below.")
    else:
        form = BlogPostForm(initial={"status": BlogPost.STATUS_PUBLISHED, "is_featured": False})

    categories = BlogCategory.objects.all().order_by("name")
    context = {
        "form": form,
        "categories": categories,
        "is_create": True,
        "page_title": "Write New Blog Post",
    }
    return render(request, "dashboard/admin_blog_form.html", context)


@admin_required
def admin_blog_edit(request, post_id):
    """Admin page to edit an existing blog post."""
    post = get_object_or_404(BlogPost, pk=post_id)

    if request.method == "POST":
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            messages.success(request, f'Blog post "{post.title}" has been updated!')
            return redirect("admin_blog_list")
        else:
            messages.error(request, "Please correct the errors in the form below.")
    else:
        form = BlogPostForm(instance=post)

    categories = BlogCategory.objects.all().order_by("name")
    context = {
        "form": form,
        "post": post,
        "categories": categories,
        "is_create": False,
        "page_title": f"Edit Post: {post.title}",
    }
    return render(request, "dashboard/admin_blog_form.html", context)


@admin_required
@require_POST
def admin_blog_delete(request, post_id):
    """Delete a blog post."""
    post = get_object_or_404(BlogPost, pk=post_id)
    title = post.title
    post.delete()
    messages.success(request, f'Blog post "{title}" was permanently deleted.')
    return redirect("admin_blog_list")


@admin_required
@require_POST
def admin_blog_toggle_status(request, post_id):
    """Quickly toggle a post status between Draft and Published."""
    post = get_object_or_404(BlogPost, pk=post_id)
    if post.status == BlogPost.STATUS_PUBLISHED:
        post.status = BlogPost.STATUS_DRAFT
        msg = f'"{post.title}" has been changed to Draft.'
    else:
        post.status = BlogPost.STATUS_PUBLISHED
        if not post.published_at:
            post.published_at = timezone.now()
        msg = f'"{post.title}" is now Published live!'
    post.save(update_fields=["status", "published_at", "updated_at"])
    messages.success(request, msg)
    return redirect("admin_blog_list")
