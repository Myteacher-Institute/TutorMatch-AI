from django.http import HttpResponse


def checkout(request, booking_id):
    return HttpResponse(f"Payment checkout for booking {booking_id} will be built by Task 5.")


def payment_success(request):
    return HttpResponse("Payment success page will be built by Task 5.")


def payment_failed(request):
    return HttpResponse("Payment failed page will be built by Task 5.")
