from .models import Payment
from django.contrib import admin



@admin.register(Payment)

class PaymentAdmin(admin.ModelAdmin):
    list_display = ("booking", "amount", "payment_status")
    list_filter = ("payment_status",)
    search_fields = ("booking", "amount")
