from tutors.models import Tutor
from django.apps import apps


def admin_badges(request):
    if not request.user.is_authenticated:
        return {"pending_verifications_count": 0, "pending_payout_count": 0}

    if not request.user.is_staff:
        return {
            "pending_verifications_count": 0,
            "pending_payout_count": 0,
            "open_support_count": 0,
        }

    count = Tutor.objects.filter(verification_status__in=["pending", "rejected"]).count()

    pending_payout_count = 0
    open_support_count = 0
    try:
        PayoutInstallment = apps.get_model("payments", "PayoutInstallment")
        pending_payout_count = PayoutInstallment.objects.filter(
            status__in=["awaiting_student", "approved", "disputed"]
        ).count()
        SupportTicket = apps.get_model("payments", "SupportTicket")
        open_support_count = SupportTicket.objects.filter(status__in=["open", "in_review"]).count()
    except (LookupError, AttributeError):
        pass

    return {
        "pending_verifications_count": count,
        "pending_payout_count": pending_payout_count,
        "open_support_count": open_support_count,
    }
