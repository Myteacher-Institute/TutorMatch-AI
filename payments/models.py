from decimal import Decimal
from django.db import models
from accounts.models import UserProfile
from tutors.models import Tutor
from bookings.models import Booking


# Create your models here.


Payment_CHOICES = [
    ("pending", "Pending"),
    ("paid", "Paid"),
    ("failed", "Failed"),
    ("released", "Released"),
    ("refunded", "Refunded"),
]


    
# Payment Model
class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    commission = models.DecimalField(max_digits=10, decimal_places=2)
    tutor_payout = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices= Payment_CHOICES, default="pending")
    flutterwave_reference = models.CharField(max_length=200, blank=True)
    flutterwave_transaction_id = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        self.commission = self.amount * Decimal('0.15')
        self.tutor_payout = self.amount * Decimal('0.85')
        super().save(*args, **kwargs)
    

    
