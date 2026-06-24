from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.models import UserProfile
from .forms import BookingForm
from .models import Booking
from tutors.models import Tutor


def _profile_for_user(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile


@login_required
def book_tutor(request, tutor_id):
    tutor = get_object_or_404(Tutor, pk=tutor_id)
    amount = tutor.hourly_rate or 0
    student_profile = _profile_for_user(request.user)

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.student = student_profile
            booking.tutor = tutor
            booking.amount = amount
            booking.save()
            messages.success(request, "Your booking request has been created.")
            return redirect("student_bookings")
    else:
        form = BookingForm(initial={"amount": amount})

    return render(
        request,
        "bookings/book_tutor.html",
        {
            "form": form,
            "tutor": tutor,
            "amount": amount,
        },
    )


@login_required
def student_bookings(request):
    student_profile = _profile_for_user(request.user)
    bookings = (
        Booking.objects.filter(student=student_profile)
        .select_related("tutor__user__user")
        .prefetch_related("payments", "reviews")
        .order_by("-booking_date", "-lesson_time")
    )
    pending_review_count = sum(
        1 for booking in bookings if booking.status == "completed" and not booking.reviews.exists()
    )
    next_booking = (
        bookings.filter(booking_date__gte=timezone.localdate())
        .exclude(status__in=["completed", "cancelled"])
        .order_by("booking_date", "lesson_time")
        .first()
    )
    return render(
        request,
        "bookings/student_bookings.html",
        {
            "bookings": bookings,
            "bookings_count": bookings.count(),
            "pending_review_count": pending_review_count,
            "next_booking": next_booking,
        },
    )


def tutor_bookings(request):
    return HttpResponse("Tutor booking requests will be built by Task 5.")
