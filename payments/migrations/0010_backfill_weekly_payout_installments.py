from datetime import timedelta
from decimal import Decimal, ROUND_CEILING

from django.db import migrations
from django.utils import timezone


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


def backfill_installments(apps, schema_editor):
    Payment = apps.get_model("payments", "Payment")
    PayoutInstallment = apps.get_model("payments", "PayoutInstallment")

    for payment in Payment.objects.select_related("booking").filter(payment_status__in=["paid", "released"]):
        booking = payment.booking
        if PayoutInstallment.objects.filter(booking=booking).exists():
            continue

        weeks = payout_period_count(booking)
        weekly_amount = (payment.amount / Decimal(weeks)).quantize(Decimal("0.01"))
        scheduled_total = Decimal("0.00")

        for week_number in range(1, weeks + 1):
            amount = payment.amount - scheduled_total if week_number == weeks else weekly_amount
            scheduled_total += amount
            period_start = booking.booking_date + timedelta(days=(week_number - 1) * 7)
            period_end = period_start + timedelta(days=6)
            auto_release_at = timezone.make_aware(
                timezone.datetime.combine(period_end, timezone.datetime.max.time())
            ) + timedelta(days=4)
            status = "released" if payment.payment_status == "released" else "scheduled"

            PayoutInstallment.objects.create(
                payment=payment,
                booking=booking,
                week_number=week_number,
                period_start=period_start,
                period_end=period_end,
                amount=amount,
                commission=amount * Decimal("0.15"),
                tutor_payout=amount * Decimal("0.85"),
                status=status,
                auto_release_at=auto_release_at,
                released_at=timezone.now() if status == "released" else None,
            )


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0009_payoutinstallment_supportticket"),
    ]

    operations = [
        migrations.RunPython(backfill_installments, migrations.RunPython.noop),
    ]
