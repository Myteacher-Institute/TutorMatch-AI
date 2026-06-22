from django.http import HttpResponse
from django.shortcuts import render,redirect
from . forms import BookingForm

def book_tutor(request, tutor_id):
    forms = BookingForm()
    if request.method == 'POST':
        forms = BookingForm(request.POST)
        if forms.is_valid():
            forms.save()
            return redirect('student_bookings')
    context = {
        'form':forms
    }
    return render(request, 'book_tutor.html', context)


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
