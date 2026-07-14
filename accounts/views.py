from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from .forms import Registration, Login
from .models import UserProfile
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db import transaction


def register(request):
    form = Registration()
    if request.method == 'POST':
        form = Registration(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            if _role_for_user(user) == UserProfile.ROLE_TUTOR:
                return redirect('tutor_profile')
            return redirect(_dashboard_for_user(user))

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    forms = Login()
    if request.method == 'POST':
        forms = Login(request, data=request.POST)
        if forms.is_valid():
            user = forms.get_user()
            auth_login(request, user)
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect(_dashboard_for_user(user))
    return render(request, 'accounts/login.html', {'form': forms})


def logout_view(request):
    auth_logout(request)
    return redirect('login')


@login_required(login_url='login')
def verify_account(request):
    profile = getattr(request.user, 'profile', None)
    if not profile:
        profile = UserProfile.objects.create(user=request.user)

    if profile.is_verified:
        return redirect(_dashboard_for_user(request.user))

    error = None
    if request.method == 'POST':
        code = request.POST.get('otp', '').strip()
        if code == '123456' or (code.isdigit() and len(code) == 6):
            profile.is_verified = True
            profile.save()
            return redirect(_dashboard_for_user(request.user))
        else:
            error = "Invalid code. Please enter '123456' or any 6-digit number."

    return render(request, 'accounts/verify.html', {'error': error})


from .decorators import student_required, _dashboard_for_user, _role_for_user
from tutors.models import Tutor, SavedTutor
from django.db.models import Count
from bookings.models import Booking
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from payments.models import PayoutInstallment, SupportTicket


@student_required
@ensure_csrf_cookie
def student_dashboard(request):
    student_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    recent_bookings = (
        Booking.objects.filter(student=student_profile)
        .select_related("tutor__user__user")
        .order_by("-created_at")[:6]
    )
    active_bookings_count = Booking.objects.filter(student=student_profile).exclude(
        status__in=["completed", "cancelled"]
    ).count()
    upcoming_lessons_count = Booking.objects.filter(
        student=student_profile,
        booking_date__gte=timezone.localdate(),
    ).exclude(status__in=["completed", "cancelled"]).count()
    completed_lessons_count = Booking.objects.filter(
        student=student_profile,
        status="completed",
    ).count()
    cancelled_lessons_count = Booking.objects.filter(
        student=student_profile,
        status="cancelled",
    ).count()

    now = timezone.now()
    start_of_week = now - timedelta(days=now.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    weekly_booking_count = Booking.objects.filter(
        student=student_profile,
        created_at__gte=start_of_week,
    ).count()
    recommended_tutors = (
        Tutor.objects.select_related("user__user")
        .filter(is_publicly_visible=True, verification_status="approved")
        .prefetch_related("subjects")
        .annotate(review_count=Count("tutor_reviews"))
        .order_by("-years_experience", "rate_amount")[:4]
    )
    return render(
        request,
        'accounts/dashboard.html',
        {
            "recommended_tutors": recommended_tutors,
            "recent_bookings": recent_bookings,
            "active_bookings_count": active_bookings_count,
            "upcoming_lessons_count": upcoming_lessons_count,
            "completed_lessons_count": completed_lessons_count,
            "cancelled_lessons_count": cancelled_lessons_count,
            "weekly_booking_count": weekly_booking_count,
            "active_tab": "dashboard",
        },
    )


@student_required
@ensure_csrf_cookie
def saved_tutors(request):
    student_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    saved = (
        SavedTutor.objects.filter(
            student=student_profile,
            tutor__is_publicly_visible=True,
            tutor__verification_status="approved",
        )
        .select_related("tutor__user__user")
        .prefetch_related("tutor__subjects")
        .order_by("-created_at")
    )
    tutors = [item.tutor for item in saved]
    return render(
        request,
        "accounts/saved_tutors.html",
        {"tutors": tutors, "active_tab": "saved_tutors"},
    )


def _delete_account_blockers(profile):
    blockers = []
    active_statuses = ["pending", "accepted"]
    active_payout_statuses = [
        PayoutInstallment.STATUS_SCHEDULED,
        PayoutInstallment.STATUS_AWAITING_STUDENT,
        PayoutInstallment.STATUS_APPROVED,
        PayoutInstallment.STATUS_DISPUTED,
    ]

    if profile.role == UserProfile.ROLE_STUDENT:
        active_bookings = Booking.objects.filter(
            student=profile,
            status__in=active_statuses,
        ).count()
        active_payouts = PayoutInstallment.objects.filter(
            booking__student=profile,
            status__in=active_payout_statuses,
        ).count()
        open_tickets = SupportTicket.objects.filter(
            booking__student=profile,
            status__in=[SupportTicket.STATUS_OPEN, SupportTicket.STATUS_IN_REVIEW],
        ).count()
    elif profile.role == UserProfile.ROLE_TUTOR:
        tutor = Tutor.objects.filter(user=profile).first()
        active_bookings = Booking.objects.filter(
            tutor=tutor,
            status__in=active_statuses,
        ).count() if tutor else 0
        active_payouts = PayoutInstallment.objects.filter(
            booking__tutor=tutor,
            status__in=active_payout_statuses,
        ).count() if tutor else 0
        open_tickets = SupportTicket.objects.filter(
            booking__tutor=tutor,
            status__in=[SupportTicket.STATUS_OPEN, SupportTicket.STATUS_IN_REVIEW],
        ).count() if tutor else 0
    else:
        active_bookings = 0
        active_payouts = 0
        open_tickets = 0

    if active_bookings:
        blockers.append(f"{active_bookings} active booking{'s' if active_bookings != 1 else ''}")
    if active_payouts:
        blockers.append(f"{active_payouts} weekly payout item{'s' if active_payouts != 1 else ''} still in progress")
    if open_tickets:
        blockers.append(f"{open_tickets} open support ticket{'s' if open_tickets != 1 else ''}")
    return blockers


@login_required(login_url="login")
def delete_account(request):
    user = request.user
    if user.is_staff or user.is_superuser:
        messages.error(request, "Staff accounts cannot be deleted from this page.")
        return redirect("admin_dashboard")

    profile, _ = UserProfile.objects.get_or_create(user=user)
    blockers = _delete_account_blockers(profile)

    if request.method == "POST":
        password = request.POST.get("password", "")
        confirmation = request.POST.get("confirmation", "").strip()

        if blockers:
            messages.error(request, "Resolve active bookings, payouts, or support tickets before deleting this account.")
            return redirect("delete_account")
        if confirmation != "DELETE":
            messages.error(request, "Type DELETE exactly to confirm account deletion.")
            return redirect("delete_account")
        if user.has_usable_password() and not user.check_password(password):
            messages.error(request, "Password is incorrect.")
            return redirect("delete_account")

        with transaction.atomic():
            user_to_delete = user
            auth_logout(request)
            user_to_delete.delete()
        messages.success(request, "Your account has been deleted.")
        return redirect("home")

    return render(
        request,
        "accounts/delete_account.html",
        {
            "active_tab": "delete_account",
            "blockers": blockers,
            "user_profile": profile,
            "tutor_profile": Tutor.objects.filter(user=profile).first() if profile.role == UserProfile.ROLE_TUTOR else None,
        },
    )


@login_required
@require_POST
def toggle_save_tutor(request, tutor_id):
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    tutor = get_object_or_404(
        Tutor,
        id=tutor_id,
        is_publicly_visible=True,
        verification_status="approved",
    )
    saved, created = SavedTutor.objects.get_or_create(
        student=user_profile, tutor=tutor
    )
    if not created:
        saved.delete()
        return JsonResponse(
            {"saved": False, "message": "Tutor removed from saved list."}
        )
    return JsonResponse({"saved": True, "message": "Tutor saved."})


