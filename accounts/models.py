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


class HomepageStatsSetting(models.Model):
    verified_tutors_offset = models.IntegerField(
        default=678,
        help_text="Starting count for Verified Tutors"
    )
    lessons_completed_offset = models.IntegerField(
        default=5000,
        help_text="Starting count for Lessons Completed"
    )
    cities_covered_offset = models.IntegerField(
        default=793,
        help_text="Starting count for Cities Covered"
    )
    parents_joined_offset = models.IntegerField(
        default=1500,
        help_text="Starting count for Parents Joined"
    )

    class Meta:
        verbose_name = "Homepage Stats Setting"
        verbose_name_plural = "Homepage Stats Settings"

    def __str__(self):
        return "Homepage Stats Configuration"

    def save(self, *args, **kwargs):
        # Enforce singleton pattern (only one instance can exist in the DB)
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        # Load the configuration or return a default model instance
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

