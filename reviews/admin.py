from .models import Review
from django.contrib import admin

@admin.register(Review)

class ReviewsAdmin(admin.ModelAdmin):
    list_display = ("booking", "rating", "review")
    list_filter = ("rating",)
    search_fields = ("booking", "review")