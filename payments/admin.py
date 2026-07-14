from .models import Payment, PayoutInstallment, SupportTicket
from django.contrib import admin



@admin.register(Payment)

class PaymentAdmin(admin.ModelAdmin):
    list_display = ("booking", "amount", "payment_status")
    list_filter = ("payment_status",)
    search_fields = ("booking", "amount")


@admin.register(PayoutInstallment)
class PayoutInstallmentAdmin(admin.ModelAdmin):
    list_display = ("booking", "week_number", "period_start", "period_end", "tutor_payout", "status")
    list_filter = ("status", "period_start")
    search_fields = ("booking__id", "booking__student__user__username", "booking__tutor__user__user__username")


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ("booking", "installment", "raised_by", "reason", "status", "created_at")
    list_filter = ("raised_by", "reason", "status")
    search_fields = ("booking__id", "message", "admin_note")
