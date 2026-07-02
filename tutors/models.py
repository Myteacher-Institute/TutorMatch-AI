from django.db import models
from accounts.models import UserProfile


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
    hourly_rate = models.PositiveIntegerField(default=0)
    years_experience = models.PositiveIntegerField(default=0)
    verification_status = models.CharField(max_length=20, default="pending")
    subjects = models.ManyToManyField("Subject", related_name="tutors", blank=True)
    bookings = models.ManyToManyField("bookings.Booking", related_name="tutors", blank=True)
    payments = models.ManyToManyField("payments.Payment", related_name="tutors", blank=True)


    # Task 3 additions
    qualifications = models.TextField(blank=True)
    is_publicly_visible = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.location}"

    @property
    def is_verified(self):
        return self.verification_status == "approved"


class TutorDocument(models.Model):

    DOCUMENT_TYPES = [
        ('government_id', 'Government ID'),
        ('selfie', 'Selfie'),
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
