import logging
import secrets

from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from .email_services import send_transactional_email
from .models import UserProfile

logger = logging.getLogger(__name__)


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


def get_admin_notification_emails():
    """
    Returns a list of (email, name) tuples for administrators.
    Queries active superusers, staff members, users with profile.role == 'admin',
    and any configured ADMIN_NOTIFICATION_EMAILS in settings.
    """
    admin_recipients = []
    seen_emails = set()

    try:
        admin_users = (
            User.objects.filter(
                Q(is_superuser=True) | Q(is_staff=True) | Q(profile__role=UserProfile.ROLE_ADMIN),
                is_active=True,
            )
            .exclude(email="")
            .distinct()
        )
        for admin_user in admin_users:
            clean_email = admin_user.email.strip().lower()
            if clean_email and clean_email not in seen_emails and "@" in clean_email:
                seen_emails.add(clean_email)
                name = admin_user.get_full_name() or admin_user.first_name or admin_user.username or "Admin"
                admin_recipients.append((admin_user.email.strip(), name))
    except Exception:
        logger.exception("Failed to query admin users for notification emails")

    configured_emails = getattr(settings, "ADMIN_NOTIFICATION_EMAILS", [])
    for email in configured_emails:
        clean_email = email.strip().lower()
        if clean_email and clean_email not in seen_emails and "@" in clean_email:
            seen_emails.add(clean_email)
            admin_recipients.append((email.strip(), "Admin"))

    return admin_recipients


def send_admin_new_tutor_notification(request, profile):
    """
    Sends an email notification to all admins when a new tutor registers.
    """
    user = profile.user
    admin_recipients = get_admin_notification_emails()
    if not admin_recipients:
        logger.warning("No admin email recipients found to notify about new tutor %s", user.username)
        return

    try:
        admin_verifications_url = request.build_absolute_uri(reverse("admin_verifications"))
    except Exception:
        site_url = getattr(settings, "SITE_URL", "https://myteacherconnect.org").rstrip("/")
        admin_verifications_url = f"{site_url}/admin-dashboard/verifications/"

    registered_time = profile.created_at if getattr(profile, "created_at", None) else timezone.now()

    context = {
        "tutor_user": user,
        "tutor_profile": profile,
        "tutor_name": _display_name(user),
        "tutor_username": user.username,
        "tutor_email": user.email,
        "tutor_phone": getattr(profile, "phone_number", "") or "Not provided",
        "registered_at": registered_time,
        "admin_verifications_url": admin_verifications_url,
        "site_url": request.build_absolute_uri("/"),
        "brand_name": "MyteacherConnect",
        "logo_url": request.build_absolute_uri("/static/images/logos/photo_2026-07-19_21-48-00.jpg"),
    }

    subject = f"⚡ Action Required: New Tutor Signup ({_display_name(user)})"
    html_body = render_to_string("emails/admin_new_tutor_signup.html", context)
    text_body = render_to_string("emails/admin_new_tutor_signup.txt", context)

    for admin_email, admin_name in admin_recipients:
        try:
            send_transactional_email(
                to_email=admin_email,
                to_name=admin_name,
                subject=subject,
                html_body=html_body,
                text_body=text_body,
                from_email=settings.ZEPTOMAIL_FROM_EMAIL,
                from_name=settings.ZEPTOMAIL_FROM_NAME,
                reply_to_email=settings.ZEPTOMAIL_REPLY_TO_EMAIL,
                reply_to_name=settings.ZEPTOMAIL_REPLY_TO_NAME,
            )
            logger.info("Sent new tutor registration notification to admin %s", admin_email)
        except Exception:
            logger.exception("Failed to send new tutor notification to admin %s", admin_email)


def send_admin_tutor_documents_submitted_notification(request, tutor_obj):
    """
    Sends an email notification to all admins when a tutor uploads verification documents.
    """
    profile = tutor_obj.user
    user = profile.user
    admin_recipients = get_admin_notification_emails()
    if not admin_recipients:
        return

    try:
        admin_verifications_url = request.build_absolute_uri(reverse("admin_verifications"))
    except Exception:
        site_url = getattr(settings, "SITE_URL", "https://myteacherconnect.org").rstrip("/")
        admin_verifications_url = f"{site_url}/admin-dashboard/verifications/"

    context = {
        "tutor_user": user,
        "tutor_profile": profile,
        "tutor_name": _display_name(user),
        "tutor_username": user.username,
        "tutor_email": user.email,
        "tutor_phone": getattr(profile, "phone_number", "") or "Not provided",
        "documents_count": tutor_obj.documents.count(),
        "submitted_at": timezone.now(),
        "admin_verifications_url": admin_verifications_url,
        "site_url": request.build_absolute_uri("/"),
        "brand_name": "MyteacherConnect",
        "logo_url": request.build_absolute_uri("/static/images/logos/photo_2026-07-19_21-48-00.jpg"),
    }

    subject = f"📄 Tutor Documents Submitted for Verification ({_display_name(user)})"
    html_body = render_to_string("emails/admin_tutor_documents_submitted.html", context)
    text_body = render_to_string("emails/admin_tutor_documents_submitted.txt", context)

    for admin_email, admin_name in admin_recipients:
        try:
            send_transactional_email(
                to_email=admin_email,
                to_name=admin_name,
                subject=subject,
                html_body=html_body,
                text_body=text_body,
                from_email=settings.ZEPTOMAIL_FROM_EMAIL,
                from_name=settings.ZEPTOMAIL_FROM_NAME,
                reply_to_email=settings.ZEPTOMAIL_REPLY_TO_EMAIL,
                reply_to_name=settings.ZEPTOMAIL_REPLY_TO_NAME,
            )
            logger.info("Sent tutor documents notification to admin %s", admin_email)
        except Exception:
            logger.exception("Failed to send tutor documents notification to admin %s", admin_email)


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
