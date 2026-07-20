from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse

from accounts.email_services import send_transactional_email
from accounts.account_emails import _display_name


def send_payment_success_email(request, booking):
    student_user = booking.student.user
    dashboard_url = request.build_absolute_uri(reverse("student_bookings"))
    
    context = {
        "user": student_user,
        "display_name": _display_name(student_user),
        "booking": booking,
        "site_url": request.build_absolute_uri("/"),
        "dashboard_url": dashboard_url,
        "support_email": settings.ZEPTOMAIL_REPLY_TO_EMAIL or "support@myteacherconnect.org",
        "logo_url": request.build_absolute_uri("/static/images/logos/myteacherconnect-logo-blue-transparent.png"),
    }
    
    send_transactional_email(
        to_email=student_user.email,
        to_name=_display_name(student_user),
        subject=f"Payment Successful - Booking #{booking.id}",
        html_body=render_to_string("emails/payment_success.html", context),
        text_body=f"Your payment for Booking #{booking.id} was successful.\nAmount: NGN {booking.amount}\nView Booking: {dashboard_url}",
        from_email=settings.ZEPTOMAIL_WELCOME_FROM_EMAIL or "no-reply@myteacherconnect.org",
        from_name=settings.ZEPTOMAIL_WELCOME_FROM_NAME or "MyteacherConnect",
        reply_to_email=settings.ZEPTOMAIL_REPLY_TO_EMAIL,
        reply_to_name=settings.ZEPTOMAIL_REPLY_TO_NAME,
    )


def send_payment_failed_email(request, booking):
    student_user = booking.student.user
    dashboard_url = request.build_absolute_uri(reverse("student_bookings"))
    
    context = {
        "user": student_user,
        "display_name": _display_name(student_user),
        "booking": booking,
        "site_url": request.build_absolute_uri("/"),
        "dashboard_url": dashboard_url,
        "support_email": settings.ZEPTOMAIL_REPLY_TO_EMAIL or "support@myteacherconnect.org",
        "logo_url": request.build_absolute_uri("/static/images/logos/myteacherconnect-logo-blue-transparent.png"),
    }
    
    send_transactional_email(
        to_email=student_user.email,
        to_name=_display_name(student_user),
        subject=f"Payment Failed - Booking #{booking.id}",
        html_body=render_to_string("emails/payment_failed.html", context),
        text_body=f"Your payment for Booking #{booking.id} failed.\nAmount Due: NGN {booking.amount}\nTry Again: {dashboard_url}",
        from_email=settings.ZEPTOMAIL_WELCOME_FROM_EMAIL or "no-reply@myteacherconnect.org",
        from_name=settings.ZEPTOMAIL_WELCOME_FROM_NAME or "MyteacherConnect",
        reply_to_email=settings.ZEPTOMAIL_REPLY_TO_EMAIL,
        reply_to_name=settings.ZEPTOMAIL_REPLY_TO_NAME,
    )
