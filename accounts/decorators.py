from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def _role_for_user(user):
    profile = getattr(user, "profile", None)
    return getattr(profile, "role", "student")


def _dashboard_for_user(user):
    if user.is_staff or user.is_superuser:
        return 'admin_dashboard'
    
    role = _role_for_user(user)
    if role == 'tutor':
        return 'tutor_dashboard'
    return 'student_dashboard'

def student_required(view_func):
    @login_required(login_url='login')
    def _wrapped_view(request, *args, **kwargs):
        role = _role_for_user(request.user)
        if role == 'student':
            return view_func(request, *args, **kwargs)
        return redirect(_dashboard_for_user(request.user))
    return _wrapped_view

def tutor_required(view_func):
    @login_required(login_url='login')
    def _wrapped_view(request, *args, **kwargs):
        role = _role_for_user(request.user)
        if role == 'tutor':
            return view_func(request, *args, **kwargs)
        return redirect(_dashboard_for_user(request.user))
    return _wrapped_view

def admin_required(view_func):
    @login_required(login_url='login')
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        role = _role_for_user(user)
        if user.is_staff or user.is_superuser or role == 'admin':
            return view_func(request, *args, **kwargs)
        return redirect(_dashboard_for_user(user))
    return _wrapped_view
