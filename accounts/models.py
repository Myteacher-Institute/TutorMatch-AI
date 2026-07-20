from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class UserProfile(models.Model):
    ROLE_STUDENT = "student"
    ROLE_TUTOR = "tutor"
    ROLE_ADMIN = "admin"

    ROLE_CHOICES = [
        (ROLE_STUDENT, "Student/Parent"),
        (ROLE_TUTOR, "Tutor"),
        (ROLE_ADMIN, "Admin"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone_number = models.CharField(max_length=15, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_STUDENT)
    is_verified = models.BooleanField(default=False)
    email_verification_code = models.CharField(max_length=6, blank=True)
    email_verification_token = models.CharField(max_length=96, blank=True)
    email_verification_sent_at = models.DateTimeField(null=True, blank=True)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.role}"

    def mark_email_verified(self):
        self.is_verified = True
        self.email_verified_at = timezone.now()
        self.email_verification_code = ""
        self.email_verification_token = ""


class SuccessStory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="success_stories")
    title = models.CharField(max_length=120)
    story = models.TextField(max_length=1200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "success stories"

    def __str__(self):
        return f"{self.author_name}: {self.title}"

    @property
    def author_name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def profile_photo(self):
        profile = getattr(self.user, "profile", None)
        tutor = getattr(profile, "tutor_profile", None) if profile else None
        return tutor.profile_photo if tutor and tutor.profile_photo else ""
