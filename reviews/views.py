from django.http import HttpResponse


def add_review(request, booking_id):
    return HttpResponse(f"Review form for booking {booking_id} will be built by Task 5.")
