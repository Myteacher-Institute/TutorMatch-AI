from django.db import models
from accounts.models import UserProfile
from tutors.models import Tutor


# Create your models here.

Booking_CHOICES = [
    ("pending", "Pending"),
    ("accepted", "Accepted"),
    ("completed", "Completed"),
    ("cancelled", "Cancelled")
]

class Booking (models.Model):
    student = models.ForeignKey("accounts.UserProfile", on_delete=models.CASCADE, related_name="student_bookings")
    tutor = models.ForeignKey("tutors.Tutor", on_delete=models.CASCADE, related_name="tutor_bookings")
    booking_date = models.DateField()
    lesson_time = models.TimeField()
    lesson_note = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices= Booking_CHOICES, default="pending")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.student} - {self.tutor} - {self.booking_date}"    
