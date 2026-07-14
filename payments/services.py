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
    weeks = payout_period_count(booking)
    weekly_amount = (payment.amount / Decimal(weeks)).quantize(Decimal("0.01"))
    scheduled_total = Decimal("0.00")

    with transaction.atomic():
        if PayoutInstallment.objects.filter(booking=booking).exists():
            return

        for week_number in range(1, weeks + 1):
            is_last = week_number == weeks
            amount = payment.amount - scheduled_total if is_last else weekly_amount
            scheduled_total += amount

            period_start = booking.booking_date + timedelta(days=(week_number - 1) * 7)
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
                amount=amount,
                commission=Decimal("0.00"),
                tutor_payout=Decimal("0.00"),
                auto_release_at=auto_release_at,
            )


def sync_due_installments():
    today = timezone.localdate()
    PayoutInstallment.objects.filter(
        status=PayoutInstallment.STATUS_SCHEDULED,
        period_end__lt=today,
    ).update(status=PayoutInstallment.STATUS_AWAITING_STUDENT)


def next_actionable_installment(booking):
    sync_due_installments()
    return (
        booking.payout_installments.filter(
            status__in=[
                PayoutInstallment.STATUS_AWAITING_STUDENT,
                PayoutInstallment.STATUS_APPROVED,
                PayoutInstallment.STATUS_DISPUTED,
            ]
        )
        .order_by("week_number")
        .first()
    )
