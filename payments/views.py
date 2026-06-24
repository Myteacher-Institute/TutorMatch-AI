from django.http import HttpResponse
from django.shortcuts import render,redirect


def payment_success(request):
    return HttpResponse("Payment success page will be built by Task 5.")


def payment_failed(request):
    return HttpResponse("Payment failed page will be built by Task 5.")

def checkout(request, booking_id):
    return HttpResponse("Checkout page will be built by Task 5.")
    
def add_review(request, booking_id):
    return HttpResponse("Review page will be built by Task 5.")


