# Generated manually for Flutterwave migration.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0006_alter_payment_payment_status"),
    ]

    operations = [
        migrations.RenameField(
            model_name="payment",
            old_name="paystack_reference",
            new_name="flutterwave_reference",
        ),
        migrations.AddField(
            model_name="payment",
            name="flutterwave_transaction_id",
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
