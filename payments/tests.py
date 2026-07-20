from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from accounts.models import UserProfile
from bookings.models import Booking
from tutors.models import Tutor

from .models import Payment, PayoutInstallment


class FakeFlutterwaveResponse:
    def __init__(self, data):
        self._data = data

    def json(self):
        return self._data


@override_settings(
    FLUTTERWAVE_SECRET_KEY="FLWSECK_TEST_test",
    FLUTTERWAVE_PUBLIC_KEY="FLWPUBK_TEST_test",
)
class PaymentVerificationTests(TestCase):
    def setUp(self):
        self.student_user = User.objects.create_user(
            username="student",
            email="student@example.com",
            password="pass12345",
        )
        self.student_profile = UserProfile.objects.create(
            user=self.student_user,
            role=UserProfile.ROLE_STUDENT,
        )
        self.tutor_user = User.objects.create_user(
            username="tutor",
            email="tutor@example.com",
            password="pass12345",
        )
        self.tutor_profile = UserProfile.objects.create(
            user=self.tutor_user,
            role=UserProfile.ROLE_TUTOR,
        )
        self.tutor = Tutor.objects.create(
            user=self.tutor_profile,
            online_class_fee=Decimal("10000"),
            physical_class_fee=Decimal("12000"),
            rate_period="weekly",
            verification_status="approved",
        )
        self.booking = Booking.objects.create(
            student=self.student_profile,
            tutor=self.tutor,
            booking_date=timezone.localdate(),
            lesson_time=timezone.now().time(),
            duration_value=1,
            duration_unit="weeks",
            rate_amount=Decimal("10000"),
            rate_period="weekly",
            class_type="online",
            amount=Decimal("10000"),
        )
        self.payment = Payment.objects.create(
            booking=self.booking,
            amount=self.booking.amount,
            payment_status="pending",
            flutterwave_reference="BOOKING-1-EXPECTED",
        )

    def _flutterwave_payload(self, *, tx_ref="BOOKING-1-EXPECTED", booking_id=None):
        return {
            "status": "success",
            "data": {
                "status": "successful",
                "currency": "NGN",
                "amount": "10000",
                "tx_ref": tx_ref,
                "meta": {"booking_id": booking_id or self.booking.id},
            },
        }

    def test_verify_payment_marks_booking_paid_when_reference_matches(self):
        self.client.login(username="student", password="pass12345")

        with patch(
            "payments.views.requests.get",
            return_value=FakeFlutterwaveResponse(self._flutterwave_payload()),
        ):
            response = self.client.get(
                reverse("payment_verify"),
                {"transaction_id": "12345", "tx_ref": "BOOKING-1-EXPECTED"},
            )

        self.assertRedirects(response, reverse("payment_success"))
        self.booking.refresh_from_db()
        self.payment.refresh_from_db()
        self.assertEqual(self.booking.status, "accepted")
        self.assertEqual(self.payment.payment_status, "paid")
        self.assertEqual(self.payment.flutterwave_transaction_id, "12345")
        self.assertTrue(PayoutInstallment.objects.filter(booking=self.booking).exists())

    def test_verify_payment_rejects_reference_mismatch(self):
        self.client.login(username="student", password="pass12345")

        with patch(
            "payments.views.requests.get",
            return_value=FakeFlutterwaveResponse(
                self._flutterwave_payload(tx_ref="BOOKING-1-WRONG")
            ),
        ):
            response = self.client.get(
                reverse("payment_verify"),
                {"transaction_id": "12345", "tx_ref": "BOOKING-1-WRONG"},
            )

        self.assertRedirects(response, reverse("payment_failed"))
        self.booking.refresh_from_db()
        self.payment.refresh_from_db()
        self.assertEqual(self.booking.status, "pending")
        self.assertEqual(self.payment.payment_status, "failed")
        self.assertFalse(PayoutInstallment.objects.filter(booking=self.booking).exists())

    def test_verify_payment_rejects_booking_for_another_student(self):
        other_user = User.objects.create_user(
            username="other-student",
            email="other@example.com",
            password="pass12345",
        )
        UserProfile.objects.create(user=other_user, role=UserProfile.ROLE_STUDENT)
        self.client.login(username="other-student", password="pass12345")

        with patch(
            "payments.views.requests.get",
            return_value=FakeFlutterwaveResponse(self._flutterwave_payload()),
        ):
            response = self.client.get(
                reverse("payment_verify"),
                {"transaction_id": "12345", "tx_ref": "BOOKING-1-EXPECTED"},
            )

        self.assertEqual(response.status_code, 404)
        self.booking.refresh_from_db()
        self.payment.refresh_from_db()
        self.assertEqual(self.booking.status, "pending")
        self.assertEqual(self.payment.payment_status, "pending")
