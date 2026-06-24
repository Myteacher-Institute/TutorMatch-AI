from django import forms
from django.contrib.auth.models import User
from .models import Booking
from django.core.exceptions import ValidationError
from datetime import date




class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [ 'booking_date', 'lesson_time', 'lesson_note', 'amount']

    def clean_booking_date(self):
        booking_date = self.cleaned_data['booking_date']
        if booking_date < date.today():
            raise ValidationError("You can't book a lesson in the past")
        return booking_date
    def clean_lesson_time(self):
        lesson_time = self.cleaned_data['lesson_time']
        if lesson_time < date.today():
            raise ValidationError("You can't book a lesson in the past")