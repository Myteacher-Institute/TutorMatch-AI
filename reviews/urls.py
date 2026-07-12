from django.urls import path

from . import views

urlpatterns = [
    path("payment/<int:booking_id>/review/", views.add_review, name="add_review"),
]
