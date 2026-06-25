from django import forms
from django.contrib.auth.models import User
from .models import Booking
from django.core.exceptions import ValidationError
from datetime import date, datetime




class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [ 'booking_date', 'lesson_time', 'lesson_note', 'amount']
        widgets = {
            'booking_date': forms.DateInput(attrs={'type': 'date'}),
            'lesson_time': forms.TimeInput(attrs={'type': 'time'}),
            'lesson_note': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Tell the tutor the subject, class level, exam goal, preferred lesson format, or any learning concerns.',
            }),
            'amount': forms.HiddenInput(),
        }

    def clean_booking_date(self):
        booking_date = self.cleaned_data['booking_date']
        if booking_date < date.today():
            raise ValidationError("You can't book a lesson in the past")
        return booking_date

    def clean_lesson_time(self):
        lesson_time = self.cleaned_data['lesson_time']
        booking_date = self.cleaned_data.get('booking_date')
        if booking_date == date.today() and lesson_time <= datetime.now().time():
            raise ValidationError("You can't book a lesson in the past")
        return lesson_time
