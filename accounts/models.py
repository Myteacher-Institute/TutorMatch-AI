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
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    last_account_details_update = models.DateTimeField(null=True, blank=True)
    pending_account_details_update = models.JSONField(null=True, blank=True)
    pending_update_effective_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.role}"

    def mark_email_verified(self):
        self.is_verified = True
        self.email_verified_at = timezone.now()
        self.email_verification_code = ""
        self.email_verification_token = ""

    def process_pending_account_details(self):
        """Auto-apply requested details when the 4-day delay expires."""
        if self.pending_account_details_update and self.pending_update_effective_at:
            if timezone.now() >= self.pending_update_effective_at:
                data = self.pending_account_details_update
                user = self.user
                if data.get("full_name"):
                    parts = data["full_name"].strip().split(maxsplit=1)
                    user.first_name = parts[0] if len(parts) > 0 else ""
                    user.last_name = parts[1] if len(parts) > 1 else ""
                if data.get("username"):
                    user.username = data["username"].strip()
                if data.get("email"):
                    user.email = data["email"].strip()
                user.save()

                if data.get("phone_number"):
                    self.phone_number = data["phone_number"].strip()

                self.pending_account_details_update = None
                self.pending_update_effective_at = None
                self.save()

    @property
    def can_update_account_details(self):
        if not self.last_account_details_update:
            return True
        from datetime import timedelta
        return timezone.now() >= self.last_account_details_update + timedelta(days=90)

    @property
    def next_allowed_account_details_update(self):
        if not self.last_account_details_update:
            return None
        from datetime import timedelta
        return self.last_account_details_update + timedelta(days=90)


from django.core.validators import MinValueValidator, MaxValueValidator


class SuccessStory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="success_stories")
    title = models.CharField(max_length=120)
    rating = models.PositiveSmallIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating out of 5 stars"
    )
    story = models.TextField(max_length=1200)
    is_hidden = models.BooleanField(default=False, help_text="Hide story from public view")
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
        if tutor and getattr(tutor, "profile_photo", None):
            return tutor.profile_photo
        avatar_num = ((self.user_id or 1) % 3) + 1
        return f"/static/images/avatars/avatar{avatar_num}.png"


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
    video_section_title = models.CharField(
        max_length=200,
        default="Discover How MyteacherConnect Works",
        help_text="Title for the homepage video section"
    )
    video_section_subtitle = models.TextField(
        default="Watch our short overview to see how our AI matching, verified background-checked tutors, and safe lesson delivery empower learning across Nigeria.",
        help_text="Subtitle description for the video section"
    )
    youtube_video_url = models.URLField(
        blank=True,
        default="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        help_text="YouTube video URL (e.g. https://www.youtube.com/watch?v=VIDEO_ID)"
    )
    video_section_active = models.BooleanField(
        default=True,
        help_text="Toggle to show or hide the video section on the homepage"
    )

    @property
    def youtube_embed_url(self):
        if not self.youtube_video_url:
            return ""
        url = str(self.youtube_video_url).strip()
        if "embed/" in url:
            return url
        video_id = ""
        if "v=" in url:
            video_id = url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in url:
            video_id = url.split("youtu.be/")[1].split("?")[0]
        elif "shorts/" in url:
            video_id = url.split("shorts/")[1].split("?")[0]
        if video_id:
            return f"https://www.youtube-nocookie.com/embed/{video_id}?rel=0"
        return url

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

