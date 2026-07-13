# Generated manually for flexible tutor pricing.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tutors", "0012_tutor_home_featured"),
    ]

    operations = [
        migrations.RenameField(
            model_name="tutor",
            old_name="hourly_rate",
            new_name="rate_amount",
        ),
        migrations.AddField(
            model_name="tutor",
            name="rate_period",
            field=models.CharField(
                choices=[("daily", "Daily"), ("weekly", "Weekly"), ("monthly", "Monthly")],
                default="weekly",
                max_length=20,
            ),
        ),
    ]
