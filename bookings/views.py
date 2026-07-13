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
    tutor = get_object_or_404(
        Tutor,
        pk=tutor_id,
        is_publicly_visible=True,
        verification_status="approved",
    )
    amount = tutor.rate_amount or 0
    student_profile = _profile_for_user(request.user)
    if amount <= 0:
        messages.error(request, "This tutor has not set a booking rate yet, so booking is unavailable.")
        return redirect("tutor_detail", tutor_id=tutor.id)

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.student = student_profile
            booking.tutor = tutor
            booking.rate_amount = tutor.rate_amount
            booking.rate_period = tutor.rate_period
            booking.amount = tutor.calculate_booking_amount(
                booking.duration_value,
                booking.duration_unit,
            )
            existing = Booking.objects.filter(
                student=student_profile,
                tutor=tutor,
                booking_date=booking.booking_date,
                lesson_time=booking.lesson_time,
                duration_value=booking.duration_value,
                duration_unit=booking.duration_unit,
                status="pending",
            ).first()
            if existing:
                messages.info(request, "You already have a pending request for this time slot.")
                return redirect("payment_checkout", booking_id=existing.id)
            booking.save()
            messages.success(request, "Your booking request has been created.")
            return redirect("payment_checkout", booking_id=booking.id)
    else:
        form = BookingForm()

    return render(
        request,
        "bookings/book_tutor.html",
        {
            "form": form,
            "tutor": tutor,
            "amount": amount,
            "rate_period": tutor.rate_period,
            "rate_period_label": tutor.rate_period_label,
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
    pending_review_count = bookings_queryset.filter(status="pending").count()
    page_obj = _paginated_bookings(request, bookings_queryset)
    pending_payment_count = 0
    for booking in page_obj:
        payments = list(booking.payments.all())
        paid_payment = next(
            (payment for payment in payments if payment.payment_status == "paid"),
            None,
        )
        latest_payment = payments[0] if payments else None
        display_payment = paid_payment or latest_payment
        display_status = display_payment.payment_status if display_payment else "pending"
        # Students should not see the internal "released" (tutor payout) state;
        # from their perspective the payment is simply paid.
        if display_status == "released":
            display_status = "paid"
            display_label = "Paid"
        else:
            display_label = display_payment.get_payment_status_display() if display_payment else "Pending"
        booking.display_payment_status = display_status
        booking.display_payment_status_label = display_label
        if display_status == "pending":
            pending_payment_count += 1
    completed_lessons_count = Booking.objects.filter(
        student=student_profile,
        status="completed",
    ).count()
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
            "pending_payment_count": pending_payment_count,
            "next_booking": next_booking,
            "completed_lessons_count": completed_lessons_count,
            "active_tab": "bookings",
        },
    )


@login_required
def tutor_bookings(request):
    tutor = get_object_or_404(Tutor, user=_profile_for_user(request.user))
    bookings_queryset = (
        Booking.objects.filter(tutor=tutor)
        .select_related("student__user")
        .prefetch_related("payments")
        .order_by("-created_at")
    )
    pending_count = bookings_queryset.filter(status="pending").count()
    accepted_count = bookings_queryset.filter(status="accepted").count()
    completed_count = bookings_queryset.filter(status="completed").count()
    page_obj = _paginated_bookings(request, bookings_queryset)

    for booking in page_obj:
        payments = list(booking.payments.all())
        paid_payment = next(
            (payment for payment in payments if payment.payment_status == "paid"),
            None,
        )
        released = next(
            (payment for payment in payments if payment.payment_status == "released"),
            None,
        )
        latest_payment = payments[0] if payments else None
        display_payment = released or paid_payment or latest_payment
        booking.display_payment_status = display_payment.payment_status if display_payment else "pending"
        booking.display_payment_status_label = (
            display_payment.get_payment_status_display() if display_payment else "Pending"
        )

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
            "tutor_profile": tutor,
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

    if status == "accepted" and booking.payments.filter(payment_status="pending").exists():
        messages.error(request, "You can only accept bookings that have been paid for.")
        return redirect("tutor_bookings")

    if status == "cancelled":
        error, refunded = _refund_booking_if_paid(booking)
        if error:
            messages.error(request, error)
            return redirect("tutor_bookings")
        if refunded:
            messages.success(request, "Booking rejected. The student's payment has been refunded.")
            return redirect("tutor_bookings")

    booking.status = status
    booking.save(update_fields=["status"])
    messages.success(request, success_message)
    return redirect("tutor_bookings")


def _refund_booking_if_paid(booking):
    """Refund a paid payment for a booking being rejected.

    Returns a tuple (error_message, refunded). On failure `error_message` is
    set so the caller can abort the cancellation. `refunded` is True when a
    payment was actually refunded.
    """
    payment = booking.payments.filter(payment_status="paid").first()
    if not payment or not payment.flutterwave_transaction_id:
        return None, False

    from payments.views import initiate_flutterwave_refund

    ok, message, _ = initiate_flutterwave_refund(payment.flutterwave_transaction_id, payment.amount)
    if not ok:
        return f"Refund failed: {message}. The booking was not rejected.", False

    payment.payment_status = "refunded"
    payment.save(update_fields=["payment_status"])
    return None, True
