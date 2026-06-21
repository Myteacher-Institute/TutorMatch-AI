from django.db import models
from django.conf import settings


class Subject(models.Model):
    subject_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.subject_name


class Tutor(models.Model):
    user = models.OneToOneField("accounts.UserProfile", on_delete=models.CASCADE, related_name="tutor_profile")
    profile_photo = models.ImageField(upload_to="tutor_photos/", blank=True, null=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=120)
    hourly_rate = models.PositiveIntegerField(default=0)
    years_experience = models.PositiveIntegerField(default=0)
    verification_status = models.CharField(max_length=20, default="pending")
    subjects = models.ManyToManyField("Subject", related_name="tutors", blank=True)

    def __str__(self):
        return f"{self.user} - {self.location}"
