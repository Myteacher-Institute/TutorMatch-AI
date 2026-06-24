from .models import Booking
from django.contrib import admin


@admin.register(Booking)

class BookingAdmin(admin.ModelAdmin):
    list_display = ("student", "tutor", "booking_date", "lesson_time", "status")
    list_filter = ("status",)
    search_fields = ("student", "tutor", "booking_date", "lesson_time")
