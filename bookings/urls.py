from django.urls import path

from . import views

urlpatterns = [
    path("book/<int:tutor_id>/", views.book_tutor, name="book_tutor"),
    path("bookings/", views.student_bookings, name="student_bookings"),
    path("tutor/bookings/", views.tutor_bookings, name="tutor_bookings"),
]
