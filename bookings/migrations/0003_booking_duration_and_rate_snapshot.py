# Generated manually for flexible booking durations.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0002_booking_created_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="booking",
            name="duration_value",
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name="booking",
            name="duration_unit",
            field=models.CharField(
                choices=[("days", "Day(s)"), ("weeks", "Week(s)"), ("months", "Month(s)")],
                default="weeks",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="booking",
            name="rate_amount",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name="booking",
            name="rate_period",
            field=models.CharField(default="weekly", max_length=20),
        ),
    ]
