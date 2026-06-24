from django.urls import path
from django.shortcuts import render 

from . import views

urlpatterns = [
    path("payment/<int:booking_id>/", views.checkout, name="payment_checkout"),
    path("payment/success/", views.payment_success, name="payment_success"),
    path("payment/failed/", views.payment_failed, name="payment_failed"),
    path("payment/<int:booking_id>/review/", views.add_review, name="add_review"),
]
