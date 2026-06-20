from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

from .models import UserProfile


class Registration(UserCreationForm):
    email = forms.EmailField(required=True)
    phonenumber = forms.CharField(
        label='Phone number',
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={
            'inputmode': 'numeric',
            'pattern': r'\d*',
        }),
        validators=[
            RegexValidator(
                regex=r'^\d{7,15}$',
                message='Enter numbers only, 7 to 15 digits.',
            )
        ],
    )
    role_selection = forms.ChoiceField(
        choices=[('student', 'Student/Parent'), ('tutor', 'Tutor')],
        required=True,
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phonenumber', 'role_selection', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already exists by another user')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    'phone_number': self.cleaned_data['phonenumber'],
                    'role': self.cleaned_data['role_selection'],
                },
            )
        return user


class Login(AuthenticationForm):
    model = User
    field = ('email', 'password')
