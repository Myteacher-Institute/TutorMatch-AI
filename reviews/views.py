from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import student_required
from bookings.models import Booking

from .forms import ReviewForm


@student_required
def add_review(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related("student", "tutor__user__user").prefetch_related("tutor__subjects"),
        id=booking_id,
        student=request.user.profile,
    )

    if booking.status != "completed":
        messages.error(request, "You can only review completed lessons.")
        return redirect("student_bookings")

    if booking.reviews.exists():
        messages.info(request, "You have already reviewed this lesson.")
        return redirect("student_bookings")

    form = ReviewForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        review = form.save(commit=False)
        review.student = request.user.profile
        review.tutor = booking.tutor
        review.booking = booking
        review.save()
        messages.success(request, "Thanks for reviewing your tutor.")
        return redirect("student_bookings")

    return render(
        request,
        "reviews/review_form.html",
        {
            "booking": booking,
            "tutor": booking.tutor,
            "form": form,
        },
    )
