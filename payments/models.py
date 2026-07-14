from decimal import Decimal
from django.db import models
from django.utils import timezone
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


class PayoutInstallment(models.Model):
    STATUS_SCHEDULED = "scheduled"
    STATUS_AWAITING_STUDENT = "awaiting_student"
    STATUS_APPROVED = "approved"
    STATUS_DISPUTED = "disputed"
    STATUS_RELEASED = "released"
    STATUS_REFUNDED = "refunded"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_SCHEDULED, "Scheduled"),
        (STATUS_AWAITING_STUDENT, "Awaiting student"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_DISPUTED, "Disputed"),
        (STATUS_RELEASED, "Released"),
        (STATUS_REFUNDED, "Refunded"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="installments")
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="payout_installments")
    week_number = models.PositiveIntegerField()
    period_start = models.DateField()
    period_end = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    commission = models.DecimalField(max_digits=10, decimal_places=2)
    tutor_payout = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=24, choices=STATUS_CHOICES, default=STATUS_SCHEDULED)
    student_satisfied_at = models.DateTimeField(blank=True, null=True)
    auto_release_at = models.DateTimeField()
    released_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("booking", "week_number")
        ordering = ["period_start", "week_number"]

    @property
    def is_auto_approved(self):
        return self.status == self.STATUS_AWAITING_STUDENT and timezone.now() >= self.auto_release_at

    def mark_approved(self):
        self.status = self.STATUS_APPROVED
        self.student_satisfied_at = timezone.now()
        self.save(update_fields=["status", "student_satisfied_at"])

    def mark_released(self):
        self.status = self.STATUS_RELEASED
        self.released_at = timezone.now()
        self.save(update_fields=["status", "released_at"])

    def save(self, *args, **kwargs):
        if self.amount is not None:
            self.commission = self.amount * Decimal("0.15")
            self.tutor_payout = self.amount * Decimal("0.85")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking #{self.booking_id} week {self.week_number} - {self.status}"


class SupportTicket(models.Model):
    ROLE_STUDENT = "student"
    ROLE_TUTOR = "tutor"
    ROLE_ADMIN = "admin"

    REASON_QUALITY = "quality"
    REASON_ATTENDANCE = "attendance"
    REASON_PAYMENT = "payment"
    REASON_SAFETY = "safety"
    REASON_OTHER = "other"

    STATUS_OPEN = "open"
    STATUS_IN_REVIEW = "in_review"
    STATUS_RESOLVED = "resolved"
    STATUS_CLOSED = "closed"

    RAISED_BY_CHOICES = [
        (ROLE_STUDENT, "Student"),
        (ROLE_TUTOR, "Tutor"),
        (ROLE_ADMIN, "Admin"),
    ]
    REASON_CHOICES = [
        (REASON_QUALITY, "Teaching quality"),
        (REASON_ATTENDANCE, "Attendance or lateness"),
        (REASON_PAYMENT, "Payment or payout"),
        (REASON_SAFETY, "Safety concern"),
        (REASON_OTHER, "Other"),
    ]
    STATUS_CHOICES = [
        (STATUS_OPEN, "Open"),
        (STATUS_IN_REVIEW, "In review"),
        (STATUS_RESOLVED, "Resolved"),
        (STATUS_CLOSED, "Closed"),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="support_tickets")
    installment = models.ForeignKey(
        PayoutInstallment,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="support_tickets",
    )
    raised_by = models.CharField(max_length=16, choices=RAISED_BY_CHOICES)
    reason = models.CharField(max_length=24, choices=REASON_CHOICES, default=REASON_OTHER)
    message = models.TextField()
    evidence_url = models.URLField(blank=True)
    status = models.CharField(max_length=24, choices=STATUS_CHOICES, default=STATUS_OPEN)
    admin_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_raised_by_display()} ticket for booking #{self.booking_id}"
