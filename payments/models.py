from django.db import models


# Create your models here.

Booking_CHOICES = [
    ("pending", "Pending"),
    ("accepted", "Accepted"),
    ("completed", "Completed"),
    ("cancelled", "Cancelled")
]

class Booking (models.Model):
    student = models.ForeignKey("accounts.UserProfile", on_delete=models.CASCADE, related_name="student_bookings")
    tutor = models.ForeignKey("accounts.UserProfile", on_delete=models.CASCADE, related_name="tutor_bookings")
    booking_date = models.DateField()
    lesson_time = models.TimeField()
    status = models.CharField(max_length=20, choices= Booking_CHOICES, default="pending")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
# Payment Model
class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    commission = models.DecimalField(max_digits=10, decimal_places=2)
    tutor_payout = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices= Booking_CHOICES, default="pending")
    paystack_reference = models.CharField(max_length=100, blank=True)
    
# Review Model

class Review(models.Model):
    student = models.ForeignKey("accounts.UserProfile", on_delete=models.CASCADE, related_name="student_reviews")
    tutor = models.ForeignKey("tutors.Tutor", on_delete=models.CASCADE, related_name="tutor_reviews")
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveIntegerField(default=0)
    review = models.TextField(blank=True)
    