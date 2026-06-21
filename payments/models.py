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

Payment_CHOICES = [
    ("pending", "Pending"),
    ("paid", "Paid"),
    ("failed", "Failed"),
]


class Booking (models.Model):
    student = models.ForeignKey("accounts.UserProfile", on_delete=models.CASCADE, related_name="student_bookings")
    tutor = models.ForeignKey("tutors.Tutor", on_delete=models.CASCADE, related_name="tutor_bookings")
    booking_date = models.DateField()
    lesson_time = models.TimeField()
    status = models.CharField(max_length=20, choices= Booking_CHOICES, default="pending")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.student} - {self.tutor} - {self.booking_date}"
    
# Payment Model
class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    commission = models.DecimalField(max_digits=10, decimal_places=2)
    tutor_payout = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices= Payment_CHOICES, default="pending")
    paystack_reference = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        self.commission = self.amount * 0.15
        self.tutor_payout = self.amount * 0.85
        super().save(*args, **kwargs)
    
# Review Model

class Review(models.Model):
    student = models.ForeignKey("accounts.UserProfile", on_delete=models.CASCADE, related_name="student_reviews")
    tutor = models.ForeignKey("tutors.Tutor", on_delete=models.CASCADE, related_name="tutor_reviews")
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveIntegerField(default=0)
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student} - {self.tutor} - {self.booking} - {self.rating}"
    