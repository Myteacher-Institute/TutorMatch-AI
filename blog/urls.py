from django.urls import path
from . import views

urlpatterns = [
    # Public Blog Views
    path("blog/", views.blog_list, name="blog_list"),
    path("blog/<slug:slug>/", views.blog_detail, name="blog_detail"),
    path("blog/category/<slug:slug>/", views.blog_category_list, name="blog_category_list"),

    # Admin Management Views
    path("admin-dashboard/blogs/", views.admin_blog_list, name="admin_blog_list"),
    path("admin-dashboard/blogs/create/", views.admin_blog_create, name="admin_blog_create"),
    path("admin-dashboard/blogs/<int:post_id>/edit/", views.admin_blog_edit, name="admin_blog_edit"),
    path("admin-dashboard/blogs/<int:post_id>/delete/", views.admin_blog_delete, name="admin_blog_delete"),
    path("admin-dashboard/blogs/<int:post_id>/toggle-status/", views.admin_blog_toggle_status, name="admin_blog_toggle_status"),
]
