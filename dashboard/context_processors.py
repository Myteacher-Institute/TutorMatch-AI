from tutors.models import Tutor


def admin_badges(request):
    if not request.user.is_authenticated:
        return {"pending_verifications_count": 0}

    if not request.user.is_staff:
        return {"pending_verifications_count": 0}

    count = Tutor.objects.filter(verification_status__in=["pending", "rejected"]).count()
    return {"pending_verifications_count": count}
