from django.urls import path
from . import views

urlpatterns = [
    path("payment/<int:booking_id>/", views.checkout, name="payment_checkout"),
    path("payment/success/", views.payment_success, name="payment_success"),
    path("payment/failed/", views.payment_failed, name="payment_failed"),
    path("payments/verify/", views.verify_payment, name="payment_verify"),
]
