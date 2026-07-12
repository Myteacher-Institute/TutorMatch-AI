from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
import requests
from django.conf import settings
from bookings.models import Booking
from .models import Payment


def payment_success(request):
    return render(request, "payments/payment_success.html")


def payment_failed(request):
    return render(request, "payments/payment_failed.html")


PAYSTACK_INIT_URL = "https://api.paystack.co/transaction/initialize"
PAYSTACK_VERIFY_URL = "https://api.paystack.co/transaction/verify/"
PAYSTACK_REFUND_URL = "https://api.paystack.co/refund"

headers = {
    "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    "Content-Type": "application/json",
}


def initiate_paystack_refund(reference, amount_kobo=None):
    """Refund a successful Paystack transaction by its reference.

    Returns a tuple (success, message, data). On success the caller should
    treat the payment as refunded.
    """
    payload = {"transaction": reference}
    if amount_kobo is not None:
        payload["amount"] = amount_kobo
    try:
        response = requests.post(PAYSTACK_REFUND_URL, json=payload, headers=headers, timeout=20)
        data = response.json()
    except requests.RequestException:
        return False, "Payment gateway is unavailable, refund could not be processed.", None

    if data.get("status"):
        return True, data.get("message", "Refund initiated."), data.get("data")

    return False, data.get("message", "Refund request failed."), None


@login_required
def checkout(request, booking_id):
    booking = get_object_or_404(
        Booking.objects.select_related("tutor__user__user", "student__user"),
        id=booking_id,
        student__user=request.user,
    )

    if request.method == "POST":
        amount_kobo = int(booking.amount * Decimal('100'))
        data = {
            "email": request.user.email,
            "amount": amount_kobo,
            "callback_url": settings.PAYSTACK_CALLBACK_URL,
            "metadata": {"booking_id": booking.id},
        }
        try:
            response = requests.post(PAYSTACK_INIT_URL, json=data, headers=headers, timeout=20)
            res_data = response.json()
        except requests.RequestException:
            messages.error(request, "Payment gateway unavailable. Please try again.")
            return redirect("payment_failed")

        if res_data.get("status"):
            return redirect(res_data["data"]["authorization_url"])

        messages.error(request, "Payment initialization failed. Please try again.")
        return redirect("payment_failed")

    commission = booking.amount * Decimal('0.15')
    tutor_payout = booking.amount - commission
    template_context = {
        "booking": booking,
        "commission": commission,
        "tutor_payout": tutor_payout,
        "tutor_subjects": booking.tutor.subjects.all(),
    }
    return render(request, "payments/checkout.html", template_context)


@login_required
def verify_payment(request):
    reference = request.GET.get("reference") or request.GET.get("trxref")
    if not reference:
        messages.error(request, "Missing payment reference.")
        return redirect("payment_failed")

    url = f"{PAYSTACK_VERIFY_URL}{reference}"
    try:
        response = requests.get(url, headers=headers, timeout=20)
        data = response.json()
    except requests.RequestException:
        messages.error(request, "Payment gateway unavailable. Please try again.")
        return redirect("payment_failed")

    if data.get("status") and data["data"]["status"] == "success":
        booking_id = data["data"]["metadata"]["booking_id"]
        booking = get_object_or_404(Booking, id=booking_id)
        amount = booking.amount
        commission = amount * Decimal('0.15')
        tutor_payout = amount * Decimal('0.85')

        existing = Payment.objects.filter(booking=booking)
        if existing.count() > 1:
            keep = existing.order_by("-created_at").first()
            existing.exclude(pk=keep.pk).delete()

        Payment.objects.update_or_create(
            booking=booking,
            defaults={
                "amount": amount,
                "commission": commission,
                "tutor_payout": tutor_payout,
                "payment_status": "paid",
                "paystack_reference": reference,
            },
        )
        messages.success(request, "Payment verified successfully.")
        return redirect("payment_success")

    messages.error(request, "Payment verification failed.")
    return redirect("payment_failed")


def add_review(request, booking_id):
    return HttpResponse("Review page will be built by Task 5.")
