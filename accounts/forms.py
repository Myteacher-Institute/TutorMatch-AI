from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, UserCreationForm
from django.contrib.auth.models import User
from django.conf import settings
from django.core.validators import RegexValidator
from django.template import loader

from .models import SuccessStory, UserProfile
from .email_services import send_transactional_email


import re


class Registration(UserCreationForm):
    full_name = forms.CharField(
        label='Full name',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Full Name'}),
    )
    username = forms.CharField(
        label='Username',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Username'}),
    )
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
        fields = ['full_name', 'username', 'email', 'phonenumber', 'role_selection', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('Username already taken by another user')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already exists by another user')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        full_name = self.cleaned_data.get('full_name', '').strip()
        parts = full_name.split(maxsplit=1)
        user.first_name = parts[0] if len(parts) > 0 else ''
        user.last_name = parts[1] if len(parts) > 1 else ''

        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['username'].strip()

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
    username = forms.CharField(
        label="Username or Email Address",
        widget=forms.TextInput(attrs={"autocomplete": "username"}),
    )

    def clean(self):
        username_or_email = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username_or_email is not None and password:
            lookup = username_or_email.strip()
            user = User.objects.filter(email__iexact=lookup).first()
            if not user:
                user = User.objects.filter(username__iexact=lookup).first()
            username = user.get_username() if user else lookup
            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password,
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class ZeptoPasswordResetForm(PasswordResetForm):
    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        subject = loader.render_to_string(subject_template_name, context)
        subject = "".join(subject.splitlines())
        context = {
            **context,
            "logo_url": f"{context['protocol']}://{context['domain']}/static/images/logos/photo_2026-07-19_21-48-00.jpg",
        }
        html_body = loader.render_to_string(email_template_name, context)
        text_body = loader.render_to_string("registration/password_reset_email.txt", context)
        send_transactional_email(
            to_email=to_email,
            to_name=context["user"].get_full_name() or context["user"].get_username(),
            subject=subject,
            html_body=html_body,
            text_body=text_body,
            from_email=settings.ZEPTOMAIL_PASSWORD_RESET_FROM_EMAIL,
            from_name=settings.ZEPTOMAIL_PASSWORD_RESET_FROM_NAME,
            reply_to_email=settings.ZEPTOMAIL_REPLY_TO_EMAIL,
            reply_to_name=settings.ZEPTOMAIL_REPLY_TO_NAME,
        )


class SuccessStoryForm(forms.ModelForm):
    RATING_CHOICES = [
        (5, "5 Stars ★★★★★ - Exceptional"),
        (4, "4 Stars ★★★★☆ - Great"),
        (3, "3 Stars ★★★☆☆ - Good"),
        (2, "2 Stars ★★☆☆☆ - Fair"),
        (1, "1 Star ★☆☆☆☆ - Poor"),
    ]
    rating = forms.TypedChoiceField(
        choices=RATING_CHOICES,
        coerce=int,
        initial=5,
        widget=forms.Select(attrs={"class": "story-rating-select"}),
    )

    class Meta:
        model = SuccessStory
        fields = ["title", "rating", "story"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Give your story a short title"}),
            "story": forms.Textarea(attrs={"placeholder": "Tell the community what changed for you...", "rows": 6}),
        }
