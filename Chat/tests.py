from datetime import date, time
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import UserProfile
from bookings.models import Booking
from tutors.models import Tutor

from .models import ChatMessage, ChatSession


class ChatViewsTests(TestCase):
    def setUp(self):
        self.student_user = User.objects.create_user(
            username="student",
            password="pass12345",
        )
        self.tutor_auth_user = User.objects.create_user(
            username="tutor",
            password="pass12345",
        )
        self.other_user = User.objects.create_user(
            username="other",
            password="pass12345",
        )

        self.student_profile = UserProfile.objects.create(
            user=self.student_user,
            role=UserProfile.ROLE_STUDENT,
        )
        self.tutor_profile = UserProfile.objects.create(
            user=self.tutor_auth_user,
            role=UserProfile.ROLE_TUTOR,
        )
        self.other_profile = UserProfile.objects.create(
            user=self.other_user,
            role=UserProfile.ROLE_STUDENT,
        )
        self.tutor = Tutor.objects.create(
            user=self.tutor_profile,
            hourly_rate=2500,
            location="Lagos",
        )
        self.booking = Booking.objects.create(
            student=self.student_profile,
            tutor=self.tutor,
            booking_date=date(2026, 7, 1),
            lesson_time=time(10, 0),
            amount=Decimal("2500.00"),
        )

    def test_chat_view_creates_session_for_booking_participants(self):
        self.client.login(username="student", password="pass12345")

        response = self.client.get(reverse("chat:chat_view", args=[self.booking.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(ChatSession.objects.filter(booking=self.booking).exists())
        self.assertContains(response, "tutor")

    def test_chat_view_rejects_users_outside_booking(self):
        self.client.login(username="other", password="pass12345")

        response = self.client.get(reverse("chat:chat_view", args=[self.booking.id]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(ChatSession.objects.filter(booking=self.booking).exists())

    def test_send_message_creates_message_and_returns_fragment(self):
        self.client.login(username="student", password="pass12345")

        response = self.client.post(
            reverse("chat:send_message", args=[self.booking.id]),
            {"message": "Hello tutor"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            ChatMessage.objects.filter(
                session__booking=self.booking,
                sender=self.student_user,
                message="Hello tutor",
            ).exists()
        )
        self.assertContains(response, "Hello tutor")

    def test_get_new_messages_returns_only_new_messages_and_marks_read(self):
        session = ChatSession.objects.create(
            booking=self.booking,
            student=self.student_user,
            tutor=self.tutor_auth_user,
        )
        old_message = ChatMessage.objects.create(
            session=session,
            sender=self.student_user,
            message="Already loaded",
        )
        new_message = ChatMessage.objects.create(
            session=session,
            sender=self.tutor_auth_user,
            message="Fresh reply",
        )

        self.client.login(username="student", password="pass12345")
        response = self.client.get(
            reverse("chat:get_new_messages", args=[self.booking.id, old_message.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Already loaded")
        self.assertContains(response, "Fresh reply")
        new_message.refresh_from_db()
        self.assertTrue(new_message.is_read)
