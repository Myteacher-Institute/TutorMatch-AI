from django.urls import path

from . import views

urlpatterns = [
     path('book/<int:tutor_id>/', views.book_tutor, name='book_tutor'),
     path('bookings/', views.student_bookings, name='student_bookings'),
     path('tutor/bookings/', views.tutor_bookings, name='tutor_bookings'),
    path("payment/<int:booking_id>/", views.checkout, name="payment_checkout"),
    path("payment/success/", views.payment_success, name="payment_success"),
    path("payment/failed/", views.payment_failed, name="payment_failed"),
    path("payment/<int:booking_id>/review/", views.add_review, name="add_review"),
]
