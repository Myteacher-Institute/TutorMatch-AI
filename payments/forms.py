from django import forms
from django.contrib.auth.models import User
from .models import Booking

class Booking (forms.form):
    model = Booking
    fields = ['tutor', 'student', 'subject', 'date', 'time', 'duration', 'price']
    
