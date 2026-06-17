from django.http import HttpResponse


def register(request):
    return HttpResponse("Registration page will be built by Task 2.")


def login_view(request):
    return HttpResponse("Login page will be built by Task 2.")


def logout_view(request):
    return HttpResponse("Logout flow will be built by Task 2.")


def verify_account(request):
    return HttpResponse("Account verification page will be built by Task 2.")


def password_reset(request):
    return HttpResponse("Password reset page will be built by Task 2.")


def student_dashboard(request):
    return HttpResponse("Student dashboard will be built by Task 2.")
