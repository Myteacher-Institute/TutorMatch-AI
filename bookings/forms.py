from django import forms
from django.contrib.auth.models import User
from .models import Booking
from payments.models import SupportTicket
from django.core.exceptions import ValidationError
from datetime import date, datetime




class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [ 'booking_date', 'lesson_time', 'duration_value', 'duration_unit', 'lesson_note']
        widgets = {
            'booking_date': forms.DateInput(attrs={'type': 'date'}),
            'lesson_time': forms.TimeInput(attrs={'type': 'time'}),
            'duration_value': forms.NumberInput(attrs={'min': 1, 'value': 1}),
            'duration_unit': forms.Select(),
            'lesson_note': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Tell the tutor the subject, class level, exam goal, preferred lesson format, or any learning concerns.',
            }),
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

    def clean_duration_value(self):
        duration_value = self.cleaned_data["duration_value"]
        if duration_value < 1:
            raise ValidationError("Duration must be at least 1.")
        return duration_value


class SupportTicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ["reason", "message", "evidence_url", "evidence_image"]
        widgets = {
            "reason": forms.Select(),
            "message": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Tell support what happened. Include attendance, lesson notes, chat details, or anything the team should review.",
            }),
            "evidence_url": forms.URLInput(attrs={
                "placeholder": "Optional evidence link: screenshot, recording, document, or meeting link",
            }),
            "evidence_image": forms.FileInput(attrs={
                "accept": "image/*",
            }),
        }

    def clean_message(self):
        message = self.cleaned_data["message"].strip()
        if len(message) < 10:
            raise ValidationError("Please add a little more detail for support.")
        return message
