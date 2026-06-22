from django import forms
from django.contrib.auth.models import User
from .models import Booking
from django.core.exceptions import ValidationError
from datetime import date




class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [ 'booking_date', 'lesson_time', 'lesson_note', 'amount']

    def clean_booking_data(self):
        bookings = self.cleaned_data['booking_date']
        if bookings < date.today():
            raise ValidationError("You can't book a lesson in the past")
