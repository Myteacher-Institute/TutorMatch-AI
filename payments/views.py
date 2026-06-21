from django.http import HttpResponse


def book_tutor(request, tutor_id):
    return HttpResponse(f"Booking tutor {tutor_id} will be built by Task 5.")


def student_bookings(request):
    return HttpResponse("Student bookings page will be built by Task 5.")

def tutor_bookings(request):
    return HttpResponse("Tutor bookings page will be built by Task 5.")

def checkout(request, booking_id):
    return HttpResponse(f"Payment checkout for booking will be built by Task 5.")


def payment_success(request):
    return HttpResponse("Payment success page will be built by Task 5.")


def payment_failed(request):
    return HttpResponse("Payment failed page will be built by Task 5.")

def add_review(request, booking_id):
    return HttpResponse("Review page will be built by Task 5.")
