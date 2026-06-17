from django.http import HttpResponse


def book_tutor(request, tutor_id):
    return HttpResponse(f"Booking page for tutor {tutor_id} will be built by Task 5.")


def student_bookings(request):
    return HttpResponse("Student booking history will be built by Task 5.")


def tutor_bookings(request):
    return HttpResponse("Tutor booking requests will be built by Task 5.")
