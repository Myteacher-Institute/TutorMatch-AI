from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from unittest.mock import patch

from .account_emails import send_verification_email, send_welcome_email
from .models import UserProfile


class EmailVerificationGateTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="unverified-student",
            email="student@example.com",
            password="pass12345",
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            role=UserProfile.ROLE_STUDENT,
            is_verified=False,
        )

    def test_unverified_user_is_redirected_from_dashboard_to_verify(self):
        self.client.login(username="unverified-student", password="pass12345")

        response = self.client.get(reverse("student_dashboard"))

        self.assertRedirects(
            response,
            f"{reverse('verify_account')}?next={reverse('student_dashboard')}",
            fetch_redirect_response=False,
        )

    def test_verified_user_can_access_dashboard(self):
        self.profile.is_verified = True
        self.profile.save(update_fields=["is_verified"])
        self.client.login(username="unverified-student", password="pass12345")

        response = self.client.get(reverse("student_dashboard"))

        self.assertEqual(response.status_code, 200)

    def test_admin_role_user_bypasses_email_verification_gate(self):
        admin_user = User.objects.create_user(
            username="role-admin",
            email="admin@example.com",
            password="pass12345",
        )
        UserProfile.objects.create(
            user=admin_user,
            role=UserProfile.ROLE_ADMIN,
            is_verified=False,
        )
        self.client.login(username="role-admin", password="pass12345")

        response = self.client.get(reverse("admin_dashboard"))

        self.assertNotEqual(response.status_code, 302)


@override_settings(
    ZEPTOMAIL_VERIFICATION_FROM_EMAIL="verification@myteacherconnect.org",
    ZEPTOMAIL_VERIFICATION_FROM_NAME="MyteacherConnect Verification",
    ZEPTOMAIL_WELCOME_FROM_EMAIL="welcome@myteacherconnect.org",
    ZEPTOMAIL_WELCOME_FROM_NAME="MyteacherConnect",
    ZEPTOMAIL_REPLY_TO_EMAIL="support@myteacherconnect.org",
    ZEPTOMAIL_REPLY_TO_NAME="MyteacherConnect Support",
)
class AccountEmailSenderTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="mail-user",
            email="mail-user@example.com",
            password="pass12345",
        )
        self.profile = UserProfile.objects.create(user=self.user)
        self.request = RequestFactory().get("/")
        self.request.user = self.user

    @patch("accounts.account_emails.send_transactional_email")
    def test_verification_email_uses_verification_sender(self, send_email):
        send_verification_email(self.request, self.profile)

        self.assertEqual(
            send_email.call_args.kwargs["from_email"],
            "verification@myteacherconnect.org",
        )
        self.assertEqual(
            send_email.call_args.kwargs["reply_to_email"],
            "support@myteacherconnect.org",
        )

    @patch("accounts.account_emails.send_transactional_email")
    def test_welcome_email_uses_welcome_sender(self, send_email):
        send_welcome_email(self.request, self.profile)

        self.assertEqual(
            send_email.call_args.kwargs["from_email"],
            "welcome@myteacherconnect.org",
        )
        self.assertEqual(
            send_email.call_args.kwargs["reply_to_email"],
            "support@myteacherconnect.org",
        )
