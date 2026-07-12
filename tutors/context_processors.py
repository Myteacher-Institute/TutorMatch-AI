from .models import SavedTutor, Tutor
from bookings.models import Booking


def saved_tutor_ids(request):
    if not request.user.is_authenticated or not hasattr(request.user, "profile"):
        return {"saved_tutor_ids": set()}

    student = request.user.profile
    ids = SavedTutor.objects.filter(
        student=student,
        tutor__is_publicly_visible=True,
        tutor__verification_status="approved",
    ).values_list("tutor_id", flat=True)
    return {"saved_tutor_ids": set(ids)}


def tutor_badges(request):
    if not request.user.is_authenticated or not hasattr(request.user, "profile"):
        return {"pending_bookings_count": 0}

    if request.user.profile.role != request.user.profile.ROLE_TUTOR:
        return {"pending_bookings_count": 0}

    try:
        tutor = Tutor.objects.get(user=request.user.profile)
    except Tutor.DoesNotExist:
        return {"pending_bookings_count": 0}

    pending = Booking.objects.filter(tutor=tutor, status="pending").count()
    return {"pending_bookings_count": pending}
