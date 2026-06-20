from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import Registration,Login
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required

def register(request):
    form = Registration()
    if request.method == 'POST':
        form = Registration(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    forms = Login()
    if request.method == 'POST':
        forms = Login(request, data=request.POST)
        if forms.is_valid():
            auth_login(request, forms.get_user())
            return redirect('student_dashboard')
    return render(request, 'accounts/login.html', {'form': forms})


def logout_view(request):
    auth_logout(request)
    return redirect('login')


def verify_account(request):
    return HttpResponse("Account verification page will be built by Task 2.")


@login_required(login_url='login')
def student_dashboard(request):
    
    return render(request, 'accounts/dashboard.html')

