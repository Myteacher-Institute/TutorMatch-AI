from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import Registration, Login
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required


def register(request):
    form = Registration()
    if request.method == 'POST':
        form = Registration(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect(_dashboard_for_user(user))

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    forms = Login()
    if request.method == 'POST':
        forms = Login(request, data=request.POST)
        if forms.is_valid():
            user = forms.get_user()
            auth_login(request, user)
            return redirect(_dashboard_for_user(user))
    return render(request, 'accounts/login.html', {'form': forms})


def logout_view(request):
    auth_logout(request)
    return redirect('login')


@login_required(login_url='login')
def verify_account(request):
    profile = getattr(request.user, 'profile', None)
    if not profile:
        profile = UserProfile.objects.create(user=request.user)

    if profile.is_verified:
        return redirect(_dashboard_for_user(request.user))

    error = None
    if request.method == 'POST':
        code = request.POST.get('otp', '').strip()
        if code == '123456' or (code.isdigit() and len(code) == 6):
            profile.is_verified = True
            profile.save()
            return redirect(_dashboard_for_user(request.user))
        else:
            error = "Invalid code. Please enter '123456' or any 6-digit number."

    return render(request, 'accounts/verify.html', {'error': error})


@login_required(login_url='login')
def student_dashboard(request):
    return render(request, 'accounts/dashboard.html')


def _dashboard_for_user(user):
    if user.is_staff or user.is_superuser:
        return 'admin_dashboard'

    role = getattr(getattr(user, 'profile', None), 'role', 'student')
    if role == 'tutor':
        return 'tutor_dashboard'
    return 'student_dashboard'
