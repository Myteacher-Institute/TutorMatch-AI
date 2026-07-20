import secrets

from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from .email_services import send_transactional_email
from .models import UserProfile


def issue_email_verification(profile):
    profile.email_verification_code = f"{secrets.randbelow(1_000_000):06d}"
    profile.email_verification_token = secrets.token_urlsafe(48)
    profile.email_verification_sent_at = None
    profile.save(
        update_fields=[
            "email_verification_code",
            "email_verification_token",
            "email_verification_sent_at",
        ]
    )
    return profile


def send_verification_email(request, profile):
    profile = issue_email_verification(profile)
    user = profile.user
    verify_url = request.build_absolute_uri(
        reverse("verify_email_token", kwargs={"token": profile.email_verification_token})
    )
    context = _base_email_context(
        request,
        user,
        profile,
        {
            "verification_code": profile.email_verification_code,
            "verify_url": verify_url,
        },
    )
    send_transactional_email(
        to_email=user.email,
        to_name=_display_name(user),
        subject="Verify your MyteacherConnect account",
        html_body=render_to_string("emails/account_verification.html", context),
        text_body=render_to_string("emails/account_verification.txt", context),
        from_email=settings.ZEPTOMAIL_VERIFICATION_FROM_EMAIL,
        from_name=settings.ZEPTOMAIL_VERIFICATION_FROM_NAME,
        reply_to_email=settings.ZEPTOMAIL_REPLY_TO_EMAIL,
        reply_to_name=settings.ZEPTOMAIL_REPLY_TO_NAME,
    )
    profile.email_verification_sent_at = timezone.now()
    profile.save(update_fields=["email_verification_sent_at"])


def send_welcome_email(request, profile):
    user = profile.user
    context = _base_email_context(
        request,
        user,
        profile,
        {
            "dashboard_url": request.build_absolute_uri(reverse(_dashboard_route(profile))),
        },
    )
    send_transactional_email(
        to_email=user.email,
        to_name=_display_name(user),
        subject="Welcome to MyteacherConnect",
        html_body=render_to_string("emails/welcome.html", context),
        text_body=render_to_string("emails/welcome.txt", context),
        from_email=settings.ZEPTOMAIL_WELCOME_FROM_EMAIL,
        from_name=settings.ZEPTOMAIL_WELCOME_FROM_NAME,
        reply_to_email=settings.ZEPTOMAIL_REPLY_TO_EMAIL,
        reply_to_name=settings.ZEPTOMAIL_REPLY_TO_NAME,
    )


def _base_email_context(request, user, profile, extra=None):
    context = {
        "user": user,
        "profile": profile,
        "display_name": _display_name(user),
        "role_label": "Tutor" if profile.role == UserProfile.ROLE_TUTOR else "Student/Parent",
        "site_url": request.build_absolute_uri("/"),
        "brand_name": "MyteacherConnect",
        "support_email": settings.ZEPTOMAIL_REPLY_TO_EMAIL or "support@myteacherconnect.org",
        "logo_url": request.build_absolute_uri("/static/images/logos/photo_2026-07-19_21-48-00.jpg"),
    }
    context.update(extra or {})
    return context


def _display_name(user):
    return user.get_full_name() or user.first_name or user.username or user.email


def _dashboard_route(profile):
    if profile.role == UserProfile.ROLE_TUTOR:
        return "tutor_dashboard"
    return "student_dashboard"
