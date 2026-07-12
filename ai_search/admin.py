from django.contrib import admin
from .models import AIConversation, AIMessage, AdminAlert


@admin.register(AIConversation)
class AIConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at", "updated_at")
    list_filter = ("created_at", "user")
    search_fields = ("user__username", "session_key")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(AIMessage)
class AIMessageAdmin(admin.ModelAdmin):
    list_display = ("conversation", "role", "created_at")
    list_filter = ("role", "created_at")
    search_fields = ("conversation__id", "content")
    readonly_fields = ("created_at",)


@admin.register(AdminAlert)
class AdminAlertAdmin(admin.ModelAdmin):
    list_display = ("alert_type", "title", "is_resolved", "created_at")
    list_filter = ("alert_type", "is_resolved", "created_at")
    search_fields = ("title", "message")
    readonly_fields = ("created_at", "error_details")
    fieldsets = (
        ("Alert Info", {"fields": ("alert_type", "title", "message")}),
        ("Status", {"fields": ("is_resolved", "resolved_at")}),
        ("Error Details", {"fields": ("error_details",), "classes": ("collapse",)}),
        ("Timestamps", {"fields": ("created_at",)}),
    )
    
    def save_model(self, request, obj, form, change):
        if obj.is_resolved and not obj.resolved_at:
            from django.utils import timezone
            obj.resolved_at = timezone.now()
        super().save_model(request, obj, form, change)
