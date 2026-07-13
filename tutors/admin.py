from django.contrib import admin
from .models import Subject, Tutor, TutorDocument

# Register your models here.


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("subject_name",)
    search_fields = ("subject_name",)


@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = ("user", "profile_photo", "bio", "location", "rate_amount", "rate_period", "years_experience", "verification_status", "is_home_featured", "home_featured_order")
    search_fields = ("user__user__username", "user__user__email", "bio", "location")
    list_filter = ("verification_status", "rate_period", "is_home_featured")


@admin.register(TutorDocument)
class TutorDocumentAdmin(admin.ModelAdmin):
    list_display = ("tutor","document_type","verification_status", "document_url", "uploaded_at")
    search_fields = ("tutor", "document_type", "verification_status")

