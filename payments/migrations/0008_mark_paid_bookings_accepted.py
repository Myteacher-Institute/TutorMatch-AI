from django.db import migrations


def mark_paid_bookings_accepted(apps, schema_editor):
    Booking = apps.get_model("bookings", "Booking")
    Payment = apps.get_model("payments", "Payment")
    paid_booking_ids = (
        Payment.objects.filter(payment_status__in=["paid", "released"])
        .values_list("booking_id", flat=True)
        .distinct()
    )
    Booking.objects.filter(id__in=paid_booking_ids, status="pending").update(status="accepted")


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("payments", "0007_flutterwave_payment_fields"),
    ]

    operations = [
        migrations.RunPython(mark_paid_bookings_accepted, noop_reverse),
    ]
