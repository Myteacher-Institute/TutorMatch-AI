from django.db import models
from accounts.models import UserProfile
from tutors.models import Tutor
from bookings.models import Booking

# Review Model

class Review(models.Model):
    student = models.ForeignKey("accounts.UserProfile", on_delete=models.CASCADE, related_name="student_reviews")
    tutor = models.ForeignKey("tutors.Tutor", on_delete=models.CASCADE, related_name="tutor_reviews")
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveIntegerField(default=0)
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student} - {self.tutor} - {self.booking} - {self.rating}"