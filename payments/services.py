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
        weeks = offer.total_weeks
        weekly_amount = offer.weekly_student_cost
        weekly_commission = offer.platform_commission_per_class * Decimal(offer.days_per_week)
        weekly_tutor_payout = offer.weekly_tutor_payout
    else:
        weeks = payout_period_count(booking)
        weekly_amount = (payment.amount / Decimal(weeks)).quantize(Decimal("0.01"))
        weekly_commission = (payment.commission / Decimal(weeks)).quantize(Decimal("0.01"))
        weekly_tutor_payout = (payment.tutor_payout / Decimal(weeks)).quantize(Decimal("0.01"))

    base_date = booking.booking_date or booking.created_at.date() if booking.created_at else timezone.localdate()

    with transaction.atomic():
        for week_number in range(1, weeks + 1):
            period_start = base_date + timedelta(days=(week_number - 1) * 7)
            period_end = period_start + timedelta(days=6)
            auto_release_at = timezone.make_aware(
                timezone.datetime.combine(period_end, timezone.datetime.max.time())
            ) + timedelta(days=SATISFACTION_WINDOW_DAYS)

            PayoutInstallment.objects.create(
                payment=payment,
                booking=booking,
                week_number=week_number,
                period_start=period_start,
                period_end=period_end,
                amount=weekly_amount,
                commission=weekly_commission,
                tutor_payout=weekly_tutor_payout,
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
