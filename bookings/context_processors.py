from accounts.models import UserProfile
from bookings.models import Booking


def pending_payment_badge(request):
    if not request.user.is_authenticated:
        return {"pending_payment_count": 0}

    profile = getattr(request.user, "profile", None)
    if not profile or profile.role != profile.ROLE_STUDENT:
        return {"pending_payment_count": 0}

    bookings = Booking.objects.filter(student=profile).prefetch_related("payments")
    count = 0
    for booking in bookings:
        payments = list(booking.payments.all())
        paid = any(p.payment_status in ("paid", "released") for p in payments)
        if not paid:
            count += 1

    return {"pending_payment_count": count}
