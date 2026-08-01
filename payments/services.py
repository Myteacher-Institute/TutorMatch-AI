from datetime import timedelta
from decimal import Decimal, ROUND_CEILING

from django.db import transaction
from django.utils import timezone

from .models import PayoutInstallment


SATISFACTION_WINDOW_DAYS = 4


def payout_period_count(booking):
    unit_weeks = {
        "days": Decimal("1") / Decimal("7"),
        "weeks": Decimal("1"),
        "months": Decimal("4"),
    }
    raw_weeks = Decimal(max(int(booking.duration_value or 1), 1)) * unit_weeks.get(
        booking.duration_unit,
        Decimal("1"),
    )
    return max(int(raw_weeks.to_integral_value(rounding=ROUND_CEILING)), 1)


def create_weekly_payout_schedule(payment):
    booking = payment.booking
    if PayoutInstallment.objects.filter(booking=booking).exists():
        return

    if booking.course_offer:
        offer = booking.course_offer
        months = getattr(offer, "duration_months", 1) or 1
        monthly_amount = offer.monthly_fee or payment.amount
        monthly_commission = (monthly_amount * Decimal("0.20")).quantize(Decimal("0.01"))
        monthly_tutor_payout = (monthly_amount * Decimal("0.80")).quantize(Decimal("0.01"))
    else:
        months = max(int(booking.duration_value or 1), 1) if booking.duration_unit == "months" else 1
        monthly_amount = (payment.amount / Decimal(months)).quantize(Decimal("0.01"))
        monthly_commission = (payment.commission / Decimal(months)).quantize(Decimal("0.01"))
        monthly_tutor_payout = (payment.tutor_payout / Decimal(months)).quantize(Decimal("0.01"))

    base_date = booking.booking_date or (booking.created_at.date() if booking.created_at else timezone.localdate())

    with transaction.atomic():
        for month_number in range(1, months + 1):
            period_start = base_date + timedelta(days=(month_number - 1) * 30)
            period_end = period_start + timedelta(days=30)
            auto_release_at = timezone.make_aware(
                timezone.datetime.combine(period_end, timezone.datetime.max.time())
            )

            PayoutInstallment.objects.create(
                payment=payment,
                booking=booking,
                week_number=month_number,
                period_start=period_start,
                period_end=period_end,
                amount=monthly_amount,
                commission=monthly_commission,
                tutor_payout=monthly_tutor_payout,
                auto_release_at=auto_release_at,
            )


def sync_due_installments():
    today = timezone.localdate()
    PayoutInstallment.objects.filter(
        status=PayoutInstallment.STATUS_SCHEDULED,
        period_end__lt=today,
    ).update(status=PayoutInstallment.STATUS_AWAITING_STUDENT)


def next_actionable_installment(booking, include_scheduled=False):
    sync_due_installments()
    statuses = [
        PayoutInstallment.STATUS_AWAITING_STUDENT,
        PayoutInstallment.STATUS_APPROVED,
        PayoutInstallment.STATUS_DISPUTED,
    ]
    if include_scheduled:
        statuses.insert(0, PayoutInstallment.STATUS_SCHEDULED)

    return (
        booking.payout_installments.filter(
            status__in=statuses
        )
        .order_by("week_number")
        .first()
    )
