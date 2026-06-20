from django import forms
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


class Registration(UserCreationForm):
    email = forms.EmailField(required=True)
    phonenumber = forms.CharField(
        max_length=15,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^\+?\d{7,15}$',
                message='Enter a valid phone number.',
            )
        ],
    )
    role_selection = forms.ChoiceField(choices=[('student', 'Student'), ('parent', 'Parent'), ('tutor', 'Tutor')], required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phonenumber', 'role_selection', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists by another user")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user
    
class Login(AuthenticationForm):
    model = User
    field = ('email','password')
