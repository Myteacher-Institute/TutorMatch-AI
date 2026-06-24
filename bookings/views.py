from django.contrib import messages
from django.contrib.auth.decorators import login_required
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


@login_required
def tutor_bookings(request):
    tutor = get_object_or_404(Tutor, user=_profile_for_user(request.user))
    bookings = (
        Booking.objects.filter(tutor=tutor)
        .select_related("student__user")
        .order_by("-booking_date", "-lesson_time")
    )
    pending_count = bookings.filter(status="pending").count()
    accepted_count = bookings.filter(status="accepted").count()
    completed_count = bookings.filter(status="completed").count()

    return render(
        request,
        "bookings/tutor_bookings.html",
        {
            "bookings": bookings,
            "bookings_count": bookings.count(),
            "pending_count": pending_count,
            "accepted_count": accepted_count,
            "completed_count": completed_count,
        },
    )


@login_required
def update_booking_status(request, booking_id, status):
    allowed_statuses = {
        "accepted": ("pending", "Booking request accepted."),
        "cancelled": ("pending", "Booking request rejected."),
        "completed": ("accepted", "Lesson marked as completed."),
    }
    required_status, success_message = allowed_statuses.get(status, (None, None))
    if request.method != "POST" or required_status is None:
        return redirect("tutor_bookings")

    tutor = get_object_or_404(Tutor, user=_profile_for_user(request.user))
    booking = get_object_or_404(Booking, pk=booking_id, tutor=tutor)
    if booking.status != required_status:
        messages.error(request, "This booking cannot be updated from its current status.")
        return redirect("tutor_bookings")

    booking.status = status
    booking.save(update_fields=["status"])
    messages.success(request, success_message)
    return redirect("tutor_bookings")
