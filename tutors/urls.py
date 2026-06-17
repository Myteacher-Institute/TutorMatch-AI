from django.urls import path

from . import views

urlpatterns = [
    path("tutor/dashboard/", views.tutor_dashboard, name="tutor_dashboard"),
    path("tutor/profile/", views.tutor_profile, name="tutor_profile"),
    path("tutor/verification/", views.tutor_verification, name="tutor_verification"),
    path("tutors/", views.tutor_list, name="tutor_list"),
    path("tutors/<int:tutor_id>/", views.tutor_detail, name="tutor_detail"),
]
