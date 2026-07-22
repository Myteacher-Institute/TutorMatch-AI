from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.models import UserProfile
from .forms import BookingForm, SupportTicketForm
from .models import Booking
from payments.models import PayoutInstallment, SupportTicket
from payments.services import next_actionable_installment, sync_due_installments
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
    student_profile = _profile_for_user(request.user)

    if request.method == "POST":
        form = BookingForm(request.POST)
        class_type = request.POST.get("class_type", "online")
        if form.is_valid():
            booking = form.save(commit=False)
            booking.student = student_profile
            booking.tutor = tutor
            booking.class_type = class_type
            rate = tutor.online_class_fee if booking.class_type == "online" else tutor.physical_class_fee
            booking.rate_amount = rate
            booking.rate_period = tutor.rate_period
            booking.amount = tutor.calculate_booking_amount(
                booking.duration_value,
                booking.duration_unit,
                class_type=booking.class_type,
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

    default_class_type = request.GET.get("class_type", "online")
    default_amount = tutor.online_class_fee if default_class_type == "online" else tutor.physical_class_fee
    return render(
        request,
        "bookings/book_tutor.html",
        {
            "form": form,
            "tutor": tutor,
            "amount": default_amount,
            "rate_period": tutor.rate_period,
            "rate_period_label": tutor.rate_period_label,
            "online_class_fee": tutor.online_class_fee,
            "physical_class_fee": tutor.physical_class_fee,
            "default_class_type": default_class_type,
        },
    )


@login_required
def student_bookings(request):
    student_profile = _profile_for_user(request.user)
    sync_due_installments()
    bookings_queryset = (
        Booking.objects.filter(student=student_profile)
        .select_related("tutor__user__user")
        .prefetch_related("payments", "reviews", "payout_installments", "support_tickets")
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
        booking.next_payout_installment = next_actionable_installment(
            booking,
            include_scheduled=settings.PAYOUT_ALLOW_EARLY_STUDENT_CONFIRM,
        )
        booking.can_confirm_payout_week = (
            booking.next_payout_installment
            and booking.next_payout_installment.status == PayoutInstallment.STATUS_AWAITING_STUDENT
        ) or (
            settings.PAYOUT_ALLOW_EARLY_STUDENT_CONFIRM
            and booking.next_payout_installment
            and booking.next_payout_installment.status == PayoutInstallment.STATUS_SCHEDULED
        )
        booking.open_support_ticket = booking.support_tickets.filter(
            status__in=[SupportTicket.STATUS_OPEN, SupportTicket.STATUS_IN_REVIEW]
        ).first()
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
    sync_due_installments()
    bookings_queryset = (
        Booking.objects.filter(tutor=tutor)
        .select_related("student__user")
        .prefetch_related("payments", "payout_installments", "support_tickets")
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
        booking.next_payout_installment = next_actionable_installment(
            booking,
            include_scheduled=settings.PAYOUT_ALLOW_EARLY_STUDENT_CONFIRM,
        )
        booking.open_support_ticket = booking.support_tickets.filter(
            status__in=[SupportTicket.STATUS_OPEN, SupportTicket.STATUS_IN_REVIEW]
        ).first()

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
    booking.payout_installments.exclude(status=PayoutInstallment.STATUS_RELEASED).update(
        status=PayoutInstallment.STATUS_REFUNDED
    )
    return None, True


@login_required
def student_confirm_payout(request, installment_id):
    if request.method != "POST":
        return redirect("student_bookings")

    student_profile = _profile_for_user(request.user)
    installment = get_object_or_404(
        PayoutInstallment.objects.select_related("booking__student"),
        pk=installment_id,
        booking__student=student_profile,
    )
    confirmable_statuses = [PayoutInstallment.STATUS_AWAITING_STUDENT]
    if settings.PAYOUT_ALLOW_EARLY_STUDENT_CONFIRM:
        confirmable_statuses.append(PayoutInstallment.STATUS_SCHEDULED)

    if installment.status not in confirmable_statuses:
        messages.error(request, "This weekly payout is not ready for student confirmation.")
        return redirect("student_bookings")

    installment.mark_approved()
    installment.mark_released()
    messages.success(
        request,
        f"Week {installment.week_number} confirmed. Tutor payout has been released automatically.",
    )
    return redirect("student_bookings")


@login_required
def student_complain_booking(request, booking_id):
    if request.method != "POST":
        return redirect("student_bookings")

    student_profile = _profile_for_user(request.user)
    booking = get_object_or_404(Booking, pk=booking_id, student=student_profile)
    installment_id = request.POST.get("installment_id")
    installment = None
    if installment_id:
        installment = get_object_or_404(PayoutInstallment, pk=installment_id, booking=booking)

    form = SupportTicketForm(request.POST, request.FILES)
    if not form.is_valid():
        messages.error(request, "Please add a reason and complaint details before submitting.")
        return redirect("student_bookings")

    ticket = form.save(commit=False)
    ticket.booking = booking
    ticket.installment = installment
    ticket.raised_by = SupportTicket.ROLE_STUDENT
    ticket.save()

    if installment and installment.status in [
        PayoutInstallment.STATUS_AWAITING_STUDENT,
        PayoutInstallment.STATUS_APPROVED,
    ]:
        installment.status = PayoutInstallment.STATUS_DISPUTED
        installment.save(update_fields=["status"])

    messages.success(request, "Your complaint has been sent to support. The related payout is on hold while the team reviews it.")
    return redirect("student_bookings")


@login_required
def tutor_complain_booking(request, booking_id):
    if request.method != "POST":
        return redirect("tutor_bookings")

    tutor = get_object_or_404(Tutor, user=_profile_for_user(request.user))
    booking = get_object_or_404(Booking, pk=booking_id, tutor=tutor)
    installment_id = request.POST.get("installment_id")
    installment = None
    if installment_id:
        installment = get_object_or_404(PayoutInstallment, pk=installment_id, booking=booking)

    form = SupportTicketForm(request.POST, request.FILES)
    if not form.is_valid():
        error_detail = "; ".join(
            f"{field}: {', '.join(errs)}" for field, errs in form.errors.items()
        )
        messages.error(request, f"Could not submit complaint — {error_detail}")
        return redirect("tutor_bookings")

    ticket = form.save(commit=False)
    ticket.booking = booking
    ticket.installment = installment
    ticket.raised_by = SupportTicket.ROLE_TUTOR
    ticket.save()

    if installment and installment.status != PayoutInstallment.STATUS_RELEASED:
        installment.status = PayoutInstallment.STATUS_DISPUTED
        installment.save(update_fields=["status"])

    messages.success(request, "Your complaint has been sent to support for review.")
    return redirect("tutor_bookings")
