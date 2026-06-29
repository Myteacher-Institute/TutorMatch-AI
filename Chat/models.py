from django.db import models
from django.contrib.auth import get_user_model
# from bookings.models import Booking # Remove direct import

User = get_user_model()

class ChatSession(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions_as_student')
    tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions_as_tutor')
    booking = models.OneToOneField('bookings.Booking', on_delete=models.SET_NULL, null=True, blank=True, related_name='chat_session') # Use string reference
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'tutor', 'booking') # A unique chat session per student-tutor-booking combination

    def __str__(self):
        return f"Chat between {self.student.username} and {self.tutor.username} for Booking {self.booking.id if self.booking else 'N/A'}"

class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Message from {self.sender.username} in {self.session}"
