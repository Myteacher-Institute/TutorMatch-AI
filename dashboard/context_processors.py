from tutors.models import Tutor
from django.apps import apps


def admin_badges(request):
    if not request.user.is_authenticated:
        return {"pending_verifications_count": 0, "pending_payout_count": 0}

    if not request.user.is_staff:
        return {"pending_verifications_count": 0, "pending_payout_count": 0}

    count = Tutor.objects.filter(verification_status__in=["pending", "rejected"]).count()

    pending_payout_count = 0
    try:
        Payment = apps.get_model("payments", "Payment")
        pending_payout_count = Payment.objects.filter(payment_status__in=["pending", "paid"]).count()
    except (LookupError, AttributeError):
        pass

    return {"pending_verifications_count": count, "pending_payout_count": pending_payout_count}
