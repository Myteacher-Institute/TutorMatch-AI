from django.urls import path

from . import views

urlpatterns = [
    path("tutor/dashboard/", views.tutor_dashboard, name="tutor_dashboard"),
    path("tutor/profile/", views.tutor_profile, name="tutor_profile"),
    path("tutor/payout/", views.tutor_payout_settings, name="tutor_payout_settings"),
    path("tutor/verification/", views.tutor_verification, name="tutor_verification"),
    path("tutor/offers/", views.course_offer_list, name="course_offer_list"),
    path("tutor/offers/create/", views.course_offer_create, name="course_offer_create"),
    path("tutor/offers/<int:offer_id>/edit/", views.course_offer_edit, name="course_offer_edit"),
    path("tutor/offers/<int:offer_id>/delete/", views.course_offer_delete, name="course_offer_delete"),
    path("tutors/", views.tutor_list, name="tutor_list"),
    path("tutors/<int:tutor_id>/", views.tutor_detail, name="tutor_detail"),
    path("courses/", views.course_list, name="course_list"),
    path("courses/<int:offer_id>/", views.course_detail, name="course_detail"),
    path("tutors/<int:tutor_id>/request-intro-call/", views.request_intro_call, name="request_intro_call"),
    path("tutor/intro-calls/", views.tutor_intro_calls, name="tutor_intro_calls"),
    path("tutor/intro-calls/<int:call_id>/update/", views.update_intro_call_status, name="update_intro_call_status"),
]
