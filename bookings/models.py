from django.db import models
from django.utils import timezone
from accounts.models import UserProfile
from tutors.models import Tutor
# from Chat.models import ChatSession # Remove this import

# Create your models here.

Booking_CHOICES = [
    ("pending", "Pending"),
    ("accepted", "Accepted"),
    ("completed", "Completed"),
    ("cancelled", "Cancelled")
]

Duration_CHOICES = [
    ("days", "Day(s)"),
    ("weeks", "Week(s)"),
    ("months", "Month(s)"),
]

class Booking (models.Model):
    student = models.ForeignKey("accounts.UserProfile", on_delete=models.CASCADE, related_name="student_bookings")
    tutor = models.ForeignKey("tutors.Tutor", on_delete=models.CASCADE, related_name="tutor_bookings")
    booking_date = models.DateField()
    lesson_time = models.TimeField()
    lesson_note = models.TextField(blank=True)
    duration_value = models.PositiveIntegerField(default=1)
    duration_unit = models.CharField(max_length=20, choices=Duration_CHOICES, default="weeks")
    rate_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rate_period = models.CharField(max_length=20, default="weekly")
    status = models.CharField(max_length=20, choices= Booking_CHOICES, default="pending")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.student} - {self.tutor} - {self.booking_date}"
