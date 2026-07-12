from django.db import models
from accounts.models import UserProfile


class SavedTutor(models.Model):
    student = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="saved_tutors",
    )
    tutor = models.ForeignKey(
        "Tutor",
        on_delete=models.CASCADE,
        related_name="saved_by",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "tutor")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student} saved {self.tutor}"


class Subject(models.Model):
    subject_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.subject_name
        
    
'''
class Booking(models.Model):
    tutor = models.ForeignKey('Tutor', on_delete=models.CASCADE, related_name='bookings')
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='student_bookings')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    booking_date = models.DateTimeField()
    status = models.CharField(max_length=20, default='pending')  # e.g., pending, confirmed, completed

    def __str__(self):
        return f"Booking: {self.student} with {self.tutor} for {self.subject} on {self.booking_date}"
    

class Payment(models.Model):
    tutor = models.ForeignKey('Tutor', on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')

    def __str__(self):
        return f"Payment of {self.amount} to {self.tutor} for booking {self.booking}"
'''


class Tutor(models.Model):
    user = models.OneToOneField("accounts.UserProfile", on_delete=models.CASCADE, related_name="tutor_profile")
    profile_photo = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=120, blank=True)
    state = models.CharField(max_length=50, blank=True)
    local_government = models.CharField(max_length=80, blank=True)
    country = models.CharField(max_length=60, blank=True, default="Nigeria")
    hourly_rate = models.PositiveIntegerField(default=0)
    years_experience = models.PositiveIntegerField(default=0)
    verification_status = models.CharField(max_length=20, default="pending")
    subjects = models.ManyToManyField("Subject", related_name="tutors", blank=True)
    bookings = models.ManyToManyField("bookings.Booking", related_name="tutors", blank=True)
    payments = models.ManyToManyField("payments.Payment", related_name="tutors", blank=True)


    # Task 3 additions
    qualifications = models.TextField(blank=True)
    is_publicly_visible = models.BooleanField(default=False)
    is_home_featured = models.BooleanField(default=False)
    home_featured_order = models.PositiveSmallIntegerField(default=0)

    # Payout account details (private — used for tutor payouts, never shown on public profile)
    account_name = models.CharField(max_length=200, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=10, blank=True)

    def save(self, *args, **kwargs):
        self.is_publicly_visible = self.verification_status == "approved"
        if kwargs.get("update_fields") is not None and "verification_status" in kwargs["update_fields"]:
            kwargs["update_fields"] = list(kwargs["update_fields"]) + ["is_publicly_visible"]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.location}"

    @property
    def is_verified(self):
        return self.verification_status == "approved"

    @property
    def first_name(self):
        return self.user.user.first_name if self.user and self.user.user else ""

    @property
    def last_name(self):
        return self.user.user.last_name if self.user and self.user.user else ""

    @property
    def get_full_name(self):
        return self.user.user.get_full_name() if self.user and self.user.user else ""

    @property
    def username(self):
        return self.user.user.username if self.user and self.user.user else ""


class TutorDocument(models.Model):

    DOCUMENT_TYPES = [
        ('government_id', 'Government ID'),
        ('nin', 'NIN Document'),
        ('certificate', 'Certificate'),
    ]

    VERIFICATION_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    tutor = models.ForeignKey(
        Tutor,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    document_url = models.URLField(blank=True)
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS,
        default='pending'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tutor} — {self.get_document_type_display()}"
