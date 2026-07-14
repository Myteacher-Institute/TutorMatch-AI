from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-dashboard/homepage-tutors/", views.homepage_tutors, name="admin_homepage_tutors"),
    path("admin-dashboard/export-weekly-report/", views.export_weekly_report, name="admin_export_weekly_report"),
    path("admin-dashboard/verifications/", views.verifications, name="admin_verifications"),
    path("admin-dashboard/users/", views.users, name="admin_users"),
    path("admin-dashboard/bookings/", views.bookings, name="admin_bookings"),
    path("admin-dashboard/support/", views.support, name="admin_support"),
    path("admin-dashboard/revenue/", views.revenue, name="admin_revenue"),
    path("terms-of-service/", views.Termsofservice, name="terms_of_service"),
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
]
