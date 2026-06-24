from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BookingForm
from tutors.models import Tutor


@login_required
def book_tutor(request, tutor_id):
    tutor = get_object_or_404(Tutor, pk=tutor_id)
    amount = tutor.hourly_rate or 0

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.student = request.user.profile
            booking.tutor = tutor
            booking.amount = amount
            booking.save()
            messages.success(request, "Your booking request has been created.")
            return redirect("student_bookings")
    else:
        form = BookingForm(initial={"amount": amount})

    return render(
        request,
        "bookings/book_tutor.html",
        {
            "form": form,
            "tutor": tutor,
            "amount": amount,
        },
    )


def student_bookings(request):
    return HttpResponse("Student booking history will be built by Task 5.")


def tutor_bookings(request):
    return HttpResponse("Tutor booking requests will be built by Task 5.")
