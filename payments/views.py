from decimal import Decimal
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
import requests
from django.conf import settings
from bookings.models import Booking
from .models import Payment
from .services import create_weekly_payout_schedule


logger = logging.getLogger(__name__)


def payment_success(request):
    return render(request, "payments/payment_success.html")


def payment_failed(request):
    return render(request, "payments/payment_failed.html")


FLUTTERWAVE_PAYMENT_URL = "https://api.flutterwave.com/v3/payments"
FLUTTERWAVE_VERIFY_URL = "https://api.flutterwave.com/v3/transactions/{transaction_id}/verify"
FLUTTERWAVE_REFUND_URL = "https://api.flutterwave.com/v3/transactions/{transaction_id}/refund"


def flutterwave_headers():
    return {
        "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",
        "Content-Type": "application/json",
    }


def flutterwave_is_configured():
    return bool(settings.FLUTTERWAVE_SECRET_KEY and settings.FLUTTERWAVE_PUBLIC_KEY)


def _upsert_booking_payment(
    booking,
    *,
    status,
    reference="",
    transaction_id="",
):
    duplicates = Payment.objects.filter(booking=booking)
    if duplicates.count() > 1:
        keep = duplicates.order_by("-created_at").first()
        duplicates.exclude(pk=keep.pk).delete()

    payment, _ = Payment.objects.update_or_create(
        booking=booking,
        defaults={
            "amount": booking.amount,
            "payment_status": status,
            "flutterwave_reference": reference,
            "flutterwave_transaction_id": transaction_id,
        },
    )
    return payment


def _payment_status_for_booking(booking):
    payment = booking.payments.order_by("-created_at").first()
    if not payment:
        return "pending"
    return payment.payment_status


def _mark_booking_paid(booking):
    if booking.status == "pending":
        booking.status = "accepted"
        booking.save(update_fields=["status"])


def _activate_platform_managed_payouts(payment):
    if payment and payment.payment_status == "paid":
        create_weekly_payout_schedule(payment)


def initiate_flutterwave_refund(transaction_id, amount=None):
    """Refund a successful Flutterwave transaction by transaction ID."""
    if str(transaction_id).startswith("DEV-"):
        return True, "Dev refund completed.", {"id": transaction_id}
    if not settings.FLUTTERWAVE_SECRET_KEY:
        return False, "Flutterwave secret key is not configured.", None

    payload = {}
    if amount is not None:
        payload["amount"] = str(amount)
    try:
        response = requests.post(
            FLUTTERWAVE_REFUND_URL.format(transaction_id=transaction_id),
            json=payload,
            headers=flutterwave_headers(),
            timeout=20,
        )
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

    if booking.payments.filter(payment_status__in=["paid", "released"]).exists():
        messages.info(request, "This booking has already been paid for.")
        return redirect("student_bookings")

    if request.method == "POST":
        if getattr(settings, "FLUTTERWAVE_ALLOW_DEV_PAYMENT", False):
            payment = _upsert_booking_payment(
                booking,
                status="paid",
                reference=f"DEV-{booking.id}",
                transaction_id=f"DEV-{booking.id}",
            )
            _activate_platform_managed_payouts(payment)
            _mark_booking_paid(booking)
            messages.success(request, "Dev payment completed. Your booking is now active.")
            return redirect("payment_success")

        if not flutterwave_is_configured():
            messages.error(request, "Flutterwave is not configured yet. Add your Flutterwave keys before accepting real payments.")
            return redirect("payment_failed")

        tx_ref = f"BOOKING-{booking.id}-{timezone_now_ref()}"
        data = {
            "tx_ref": tx_ref,
            "amount": str(booking.amount),
            "currency": "NGN",
            "redirect_url": request.build_absolute_uri(reverse("payment_verify")),
            "customer": {
                "email": request.user.email or f"{request.user.username}@example.com",
                "name": request.user.get_full_name() or request.user.username,
            },
            "meta": {"booking_id": booking.id},
            "customizations": {
                "title": "MyteacherConnect Booking",
                "description": f"Lesson booking #{booking.id}",
                "logo": request.build_absolute_uri("/static/images/logos/myteacherconnect-logo-blue-transparent.png"),
            },
        }
        try:
            _upsert_booking_payment(booking, status="pending", reference=tx_ref)
            response = requests.post(FLUTTERWAVE_PAYMENT_URL, json=data, headers=flutterwave_headers(), timeout=20)
            res_data = response.json()
        except requests.RequestException:
            logger.exception("Flutterwave initialization failed for booking %s", booking.id)
            messages.error(request, "Payment gateway unavailable. Please try again.")
            return redirect("payment_failed")
        except ValueError:
            logger.exception("Flutterwave returned invalid JSON during initialization for booking %s", booking.id)
            messages.error(request, "Payment gateway returned an invalid response. Please try again.")
            return redirect("payment_failed")

        payment_link = (res_data.get("data") or {}).get("link")
        if res_data.get("status") == "success" and payment_link:
            return redirect(payment_link)

        _upsert_booking_payment(booking, status="failed", reference=tx_ref)
        logger.warning("Flutterwave initialization rejected booking %s: %s", booking.id, res_data)
        messages.error(request, res_data.get("message") or "Payment initialization failed. Please try again.")
        return redirect("payment_failed")

    commission = booking.amount * Decimal('0.15')
    tutor_payout = booking.amount - commission
    template_context = {
        "booking": booking,
        "commission": commission,
        "tutor_payout": tutor_payout,
        "tutor_subjects": booking.tutor.subjects.all(),
        "flutterwave_ready": flutterwave_is_configured(),
        "dev_payment_enabled": bool(getattr(settings, "FLUTTERWAVE_ALLOW_DEV_PAYMENT", False)),
        "payment_status": _payment_status_for_booking(booking),
    }
    return render(request, "payments/checkout.html", template_context)


@login_required
def verify_payment(request):
    status = request.GET.get("status")
    transaction_id = request.GET.get("transaction_id")
    tx_ref = request.GET.get("tx_ref")
    if status == "cancelled":
        messages.error(request, "Payment was cancelled.")
        return redirect("payment_failed")
    if not transaction_id:
        messages.error(request, "Missing payment reference.")
        return redirect("payment_failed")
    if not settings.FLUTTERWAVE_SECRET_KEY:
        messages.error(request, "Flutterwave is not configured.")
        return redirect("payment_failed")

    try:
        response = requests.get(
            FLUTTERWAVE_VERIFY_URL.format(transaction_id=transaction_id),
            headers=flutterwave_headers(),
            timeout=20,
        )
        data = response.json()
    except requests.RequestException:
        logger.exception("Flutterwave verification request failed for transaction %s", transaction_id)
        messages.error(request, "Payment gateway unavailable. Please try again.")
        return redirect("payment_failed")
    except ValueError:
        logger.exception("Flutterwave returned invalid JSON during verification for transaction %s", transaction_id)
        messages.error(request, "Payment gateway returned an invalid response. Please try again.")
        return redirect("payment_failed")

    payment_data = data.get("data") or {}
    meta = payment_data.get("meta") or {}
    if (
        data.get("status") == "success"
        and payment_data.get("status") == "successful"
        and str(payment_data.get("currency", "")).upper() == "NGN"
    ):
        booking_id = meta.get("booking_id")
        booking = get_object_or_404(
            Booking,
            id=booking_id,
            student__user=request.user,
        )
        payment = booking.payments.order_by("-created_at").first()
        expected_ref = payment.flutterwave_reference if payment else ""
        returned_ref = tx_ref or payment_data.get("tx_ref", "")
        if expected_ref and returned_ref and expected_ref != returned_ref:
            logger.warning(
                "Flutterwave reference mismatch for booking %s: expected %s, returned %s",
                booking.id,
                expected_ref,
                returned_ref,
            )
            _upsert_booking_payment(booking, status="failed", reference=returned_ref, transaction_id=str(transaction_id))
            messages.error(request, "Payment reference did not match this booking.")
            return redirect("payment_failed")
        amount = booking.amount
        if Decimal(str(payment_data.get("amount", "0"))) < amount:
            _upsert_booking_payment(booking, status="failed", reference=returned_ref, transaction_id=str(transaction_id))
            messages.error(request, "Payment amount did not match the booking amount.")
            return redirect("payment_failed")

        paid_payment = _upsert_booking_payment(
            booking,
            status="paid",
            reference=returned_ref,
            transaction_id=str(transaction_id),
        )
        _activate_platform_managed_payouts(paid_payment)
        _mark_booking_paid(booking)
        messages.success(request, "Payment verified successfully.")
        return redirect("payment_success")

    if tx_ref:
        booking_id = str(tx_ref).split("-")[1] if str(tx_ref).startswith("BOOKING-") and "-" in str(tx_ref) else None
        if booking_id:
            booking = Booking.objects.filter(id=booking_id, student__user=request.user).first()
            if booking:
                _upsert_booking_payment(booking, status="failed", reference=tx_ref, transaction_id=str(transaction_id))
    messages.error(request, "Payment verification failed.")
    return redirect("payment_failed")


def timezone_now_ref():
    from django.utils import timezone

    return timezone.now().strftime("%Y%m%d%H%M%S")



