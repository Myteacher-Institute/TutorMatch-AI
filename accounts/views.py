from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import render, redirect
from .forms import Registration, Login
from .models import UserProfile
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required


def register(request):
    form = Registration()
    if request.method == 'POST':
        form = Registration(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
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


from .decorators import student_required, _dashboard_for_user
from tutors.models import Tutor
from django.db.models import Count
from bookings.models import Booking


@student_required
def student_dashboard(request):
    student_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    recent_bookings = (
        Booking.objects.filter(student=student_profile)
        .select_related("tutor__user__user")
        .order_by("-created_at")[:4]
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
    recommended_tutors = (
        Tutor.objects.select_related("user__user")
        .filter(is_publicly_visible=True)
        .prefetch_related("subjects")
        .annotate(review_count=Count("tutor_reviews"))
        .order_by("-years_experience", "hourly_rate")[:3]
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
        },
    )
