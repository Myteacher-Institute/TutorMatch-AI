from django.contrib import admin

from .models import UserProfile, HomepageStatsSetting


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone_number', 'is_verified', 'created_at')
    list_filter = ('role', 'is_verified')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'phone_number')


@admin.register(HomepageStatsSetting)
class HomepageStatsSettingAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'verified_tutors_offset', 'lessons_completed_offset', 'cities_covered_offset')

    def has_add_permission(self, request):
        # Allow adding only if there's no instance yet
        return not HomepageStatsSetting.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Do not allow deletion of the configuration instance
        return False

