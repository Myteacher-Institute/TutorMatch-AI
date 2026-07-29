from decimal import Decimal, ROUND_CEILING
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
    RATE_PERIOD_CHOICES = [
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
    ]
    RATE_PERIOD_DAYS = {
        "daily": Decimal("1"),
        "weekly": Decimal("7"),
        "monthly": Decimal("30"),
    }

    user = models.OneToOneField("accounts.UserProfile", on_delete=models.CASCADE, related_name="tutor_profile")
    profile_photo = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=120, blank=True)
    state = models.CharField(max_length=50, blank=True)
    local_government = models.CharField(max_length=80, blank=True)
    country = models.CharField(max_length=60, blank=True, default="Nigeria")
    rate_amount = models.PositiveIntegerField(default=0)
    rate_period = models.CharField(max_length=20, choices=RATE_PERIOD_CHOICES, default="weekly")
    online_class_fee = models.PositiveIntegerField(default=0)
    physical_class_fee = models.PositiveIntegerField(default=0)
    years_experience = models.PositiveIntegerField(default=0)
    verification_status = models.CharField(max_length=20, default="pending")
    subjects = models.ManyToManyField("Subject", related_name="tutors", blank=True)
    bookings = models.ManyToManyField("bookings.Booking", related_name="tutors", blank=True)
    payments = models.ManyToManyField("payments.Payment", related_name="tutors", blank=True)


    # Task 3 additions
    qualifications = models.TextField(blank=True)
    languages_spoken = models.CharField(max_length=200, blank=True, help_text="e.g. English, Yoruba, French")
    address = models.TextField(blank=True, help_text="Full address")
    teaching_mode = models.CharField(
        max_length=20,
        choices=[("online", "Online"), ("physical", "Physical"), ("both", "Both")],
        default="both",
    )
    is_publicly_visible = models.BooleanField(default=False)
    is_home_featured = models.BooleanField(default=False)
    home_featured_order = models.PositiveSmallIntegerField(default=0)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("tutor_detail", kwargs={"tutor_id": self.pk})

    # Payout Settings
    payout_method = models.CharField(
        max_length=30,
        choices=[("bank_transfer", "Bank Transfer"), ("mobile_money", "Mobile Money"), ("wallet", "Wallet")],
        default="bank_transfer",
    )
    bank_name = models.CharField(max_length=100, blank=True)
    account_name = models.CharField(max_length=200, blank=True)
    account_number = models.CharField(max_length=20, blank=True)
    payout_schedule = models.CharField(
        max_length=20,
        choices=[("monthly", "Monthly (Recommended)"), ("biweekly", "Bi-weekly")],
        default="monthly",
    )

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

    @property
    def active_course_offers(self):
        return self.course_offers.filter(is_active=True)

    @property
    def active_courses_count(self):
        return self.active_course_offers.count()

    @property
    def min_course_price(self):
        offers = self.active_course_offers
        if offers.exists():
            return min(o.monthly_fee for o in offers)
        return None

    @property
    def starting_course_price_display(self):
        offers = self.active_course_offers
        if offers.exists():
            min_offer = min(offers, key=lambda o: o.monthly_fee)
            return f"From {min_offer.currency_symbol}{min_offer.monthly_fee:,.0f}/mo"
        if self.rate_amount > 0:
            return f"₦{self.rate_amount:,.0f}/mo"
        return "Services Available"

    @property
    def rate_display(self):
        return self.starting_course_price_display

    # Financial & Payout Dashboard Helper Properties
    @property
    def current_balance(self):
        from payments.models import PayoutInstallment
        released = PayoutInstallment.objects.filter(
            booking__tutor=self,
            status=PayoutInstallment.STATUS_RELEASED,
        ).aggregate(total=models.Sum("tutor_payout"))["total"] or Decimal("0.00")
        return released

    @property
    def pending_earnings(self):
        from payments.models import PayoutInstallment
        pending = PayoutInstallment.objects.filter(
            booking__tutor=self,
            status=PayoutInstallment.STATUS_SCHEDULED,
        ).aggregate(total=models.Sum("tutor_payout"))["total"] or Decimal("0.00")
        return pending

    @property
    def total_paid_out(self):
        return self.current_balance

    @property
    def next_payout_date(self):
        from django.utils import timezone
        import datetime
        now = timezone.localdate()
        if now.day < 5:
            return datetime.date(now.year, now.month, 5)
        else:
            month = now.month + 1 if now.month < 12 else 1
            year = now.year + 1 if now.month == 12 else now.year
            return datetime.date(year, month, 5)


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


class CourseOffer(models.Model):
    LEVEL_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
        ("all", "All Levels"),
    ]

    DELIVERY_MODE_CHOICES = [
        ("online", "Online"),
        ("physical", "Physical"),
        ("both", "Both (Online & Physical)"),
    ]

    ONLINE_PLATFORM_CHOICES = [
        ("google_meet", "Google Meet"),
        ("zoom", "Zoom"),
        ("teams", "Microsoft Teams"),
        ("other", "Other Platform"),
    ]

    CURRENCY_CHOICES = [
        ("NGN", "₦ - Nigerian Naira (NGN)"),
        ("USD", "$ - US Dollar (USD)"),
        ("GBP", "£ - British Pound (GBP)"),
        ("EUR", "€ - Euro (EUR)"),
    ]

    CURRENCY_SYMBOLS = {
        "NGN": "₦",
        "USD": "$",
        "GBP": "£",
        "EUR": "€",
    }

    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name="course_offers")
    title = models.CharField(max_length=200, help_text="Subject / Course Title (e.g. Graphics Design, Mathematics)")
    category = models.CharField(max_length=100, blank=True, default="Digital Skills", help_text="e.g. Digital Skills, Academics, Tech")
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="beginner")
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, related_name="course_offers")
    cover_image = models.URLField(blank=True, default="", help_text="Image URL for course cover")
    cover_image_file = models.ImageField(upload_to="course_covers/", blank=True, null=True, help_text="Upload course cover image")

    # Monthly Pricing & Duration Model
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("25000.00"), help_text="Monthly Fee (₦)")
    duration_months = models.PositiveSmallIntegerField(default=1, help_text="Course duration in months (1, 2, 3, 6)")
    sessions_per_week = models.PositiveSmallIntegerField(default=3, help_text="Sessions per Week (e.g. 3)")
    hours_per_session = models.PositiveSmallIntegerField(default=2, help_text="Hours per Session (e.g. 2)")
    max_students = models.PositiveSmallIntegerField(default=5, help_text="Maximum Students (1 for Private, 5, 10, 20)")
    currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES, default="NGN")

    # Delivery & Schedule
    delivery_mode = models.CharField(max_length=20, choices=DELIVERY_MODE_CHOICES, default="online")
    online_platform = models.CharField(max_length=30, choices=ONLINE_PLATFORM_CHOICES, blank=True, default="google_meet")
    physical_location = models.TextField(blank=True, default="", help_text="Address details if Physical class")
    schedule_days_times = models.CharField(max_length=250, blank=True, default="Mondays & Wednesdays, 4:00 PM - 6:00 PM", help_text="e.g. Mondays & Wednesdays, 4:00 PM - 6:00 PM")

    # Details & Description
    description = models.TextField(help_text="Detailed description & what students will learn")
    rules = models.TextField(blank=True, default="", help_text="Class guidelines & rules")
    requirements = models.TextField(blank=True, default="", help_text="Prerequisites & required items")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} by {self.tutor.get_full_name or self.tutor.user.user.username}"

    @property
    def currency_symbol(self):
        return self.CURRENCY_SYMBOLS.get(self.currency, "₦")

    @property
    def cover_image_url(self):
        if self.cover_image_file:
            return self.cover_image_file.url
        if self.cover_image:
            return self.cover_image
        return ""

    @property
    def total_course_price(self):
        return self.monthly_fee * Decimal(max(1, self.duration_months))

    @property
    def total_course_fee(self):
        return self.total_course_price

    @property
    def total_weeks(self):
        return max(1, self.duration_months * 4)

    @property
    def daily_rate(self):
        sessions_per_month = max(1, self.sessions_per_week * 4)
        return (self.monthly_fee / Decimal(sessions_per_month)).quantize(Decimal("1.00"), rounding=ROUND_CEILING)

    @property
    def days_per_week(self):
        return self.sessions_per_week

    @property
    def weekly_student_cost(self):
        return self.daily_rate * Decimal(self.days_per_week)

    @property
    def platform_commission_per_class(self):
        # ₦500 or equivalent base commission
        if self.currency == "USD":
            return Decimal("0.50")
        elif self.currency == "GBP":
            return Decimal("0.40")
        elif self.currency == "EUR":
            return Decimal("0.45")
        return Decimal("500.00")

    @property
    def tutor_net_daily_rate(self):
        return max(Decimal("0.00"), self.daily_rate - self.platform_commission_per_class)

    @property
    def weekly_tutor_payout(self):
        return self.tutor_net_daily_rate * Decimal(self.days_per_week)

    @property
    def total_tutor_payout(self):
        return self.weekly_tutor_payout * Decimal(self.total_weeks)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("course_detail", kwargs={"offer_id": self.pk})

