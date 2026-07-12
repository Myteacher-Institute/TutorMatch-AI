from django.contrib import admin
from .models import Subject, Tutor, TutorDocument

# Register your models here.


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("subject_name",)
    search_fields = ("subject_name",)


@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = ("user", "profile_photo", "bio", "location", "hourly_rate", "years_experience", "verification_status")
    search_fields = ("user__user__username", "user__user__email", "bio", "location")
    list_filter = ("verification_status",)


@admin.register(TutorDocument)
class TutorDocumentAdmin(admin.ModelAdmin):
    list_display = ("tutor","document_type","verification_status", "document_url", "uploaded_at")
    search_fields = ("tutor", "document_type", "verification_status")