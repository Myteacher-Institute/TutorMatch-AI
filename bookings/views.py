from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.models import UserProfile
from .forms import BookingForm
from .models import Booking
from tutors.models import Tutor


BOOKINGS_PER_PAGE = 10


def _profile_for_user(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile


def _paginated_bookings(request, bookings):
    paginator = Paginator(bookings, BOOKINGS_PER_PAGE)
    return paginator.get_page(request.GET.get("page"))


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
            return redirect("payment_checkout", booking_id=booking.id)
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
    bookings_queryset = (
        Booking.objects.filter(student=student_profile)
        .select_related("tutor__user__user")
        .prefetch_related("payments", "reviews")
        .order_by("-created_at")
    )
    pending_review_count = (
        bookings_queryset.filter(status="completed")
        .exclude(reviews__student=student_profile)
        .distinct()
        .count()
    )
    page_obj = _paginated_bookings(request, bookings_queryset)
    for booking in page_obj:
        payments = list(booking.payments.all())
        paid_payment = next(
            (payment for payment in payments if payment.payment_status == "paid"),
            None,
        )
        latest_payment = payments[0] if payments else None
        display_payment = paid_payment or latest_payment
        booking.display_payment_status = display_payment.payment_status if display_payment else "pending"
        booking.display_payment_status_label = (
            display_payment.get_payment_status_display() if display_payment else "Pending"
        )
    next_booking = (
        bookings_queryset.filter(booking_date__gte=timezone.localdate())
        .exclude(status__in=["completed", "cancelled"])
        .order_by("booking_date", "lesson_time")
        .first()
    )
    return render(
        request,
        "bookings/student_bookings.html",
        {
            "bookings": page_obj,
            "bookings_count": page_obj.paginator.count,
            "page_obj": page_obj,
            "pending_review_count": pending_review_count,
            "next_booking": next_booking,
            "active_tab": "bookings",
        },
    )


@login_required
def tutor_bookings(request):
    tutor = get_object_or_404(Tutor, user=_profile_for_user(request.user))
    bookings_queryset = (
        Booking.objects.filter(tutor=tutor)
        .select_related("student__user")
        .order_by("-created_at")
    )
    pending_count = bookings_queryset.filter(status="pending").count()
    accepted_count = bookings_queryset.filter(status="accepted").count()
    completed_count = bookings_queryset.filter(status="completed").count()
    page_obj = _paginated_bookings(request, bookings_queryset)

    return render(
        request,
        "bookings/tutor_bookings.html",
        {
            "bookings": page_obj,
            "bookings_count": page_obj.paginator.count,
            "page_obj": page_obj,
            "pending_count": pending_count,
            "accepted_count": accepted_count,
            "completed_count": completed_count,
            "active_tab": "bookings",
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
