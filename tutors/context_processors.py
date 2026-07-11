from .models import SavedTutor


def saved_tutor_ids(request):
    if not request.user.is_authenticated or not hasattr(request.user, "profile"):
        return {"saved_tutor_ids": set()}

    student = request.user.profile
    ids = SavedTutor.objects.filter(student=student).values_list(
        "tutor_id", flat=True
    )
    return {"saved_tutor_ids": set(ids)}
