from django.shortcuts import redirect
from django.urls import reverse


class EmailVerificationRequiredMiddleware:
    protected_prefixes = (
        "/dashboard/",
        "/bookings/",
        "/payment/",
        "/payments/",
        "/chat/",
        "/student/",
        "/tutor/",
        "/saved-tutors/",
        "/delete-account/",
    )

    allowed_prefixes = (
        "/verify/",
        "/logout/",
        "/login/",
        "/register/",
        "/admin/",
        "/static/",
        "/media/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        path = request.path_info
        if (
            user.is_authenticated
            and not user.is_staff
            and not user.is_superuser
            and self._is_protected_path(path)
            and not self._is_allowed_path(path)
        ):
            profile = getattr(user, "profile", None)
            if profile and profile.role == profile.ROLE_ADMIN:
                return self.get_response(request)
            if profile and not profile.is_verified:
                return redirect(f"{reverse('verify_account')}?next={path}")

        return self.get_response(request)

    def _is_protected_path(self, path):
        return any(path.startswith(prefix) for prefix in self.protected_prefixes)

    def _is_allowed_path(self, path):
        return any(path.startswith(prefix) for prefix in self.allowed_prefixes)
