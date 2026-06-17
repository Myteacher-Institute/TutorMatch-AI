from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render


def home(request):
    featured_tutors = [
        {"name": "Amina Johnson", "subject": "Mathematics", "location": "GRA", "rate": "10000"},
        {"name": "Chinedu Okoro", "subject": "Physics", "location": "Rumuola", "rate": "12000"},
        {"name": "Simi Williams", "subject": "English", "location": "Trans Amadi", "rate": "9000"},
    ]
    return render(request, "home.html", {"featured_tutors": featured_tutors})


def about(request):
    return render(request, "about.html")


def contact(request):
    return render(request, "contact.html")


def staff_required(user):
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(staff_required)
def admin_dashboard(request):
    metrics = {
        "total_tutors": 0,
        "total_students": 0,
        "total_bookings": 0,
        "total_revenue": "0",
    }
    return render(request, "dashboard/admin_dashboard.html", {"metrics": metrics})


@login_required
@user_passes_test(staff_required)
def verifications(request):
    return render(request, "dashboard/verifications.html")


@login_required
@user_passes_test(staff_required)
def users(request):
    return render(request, "dashboard/users.html")


@login_required
@user_passes_test(staff_required)
def bookings(request):
    return render(request, "dashboard/bookings.html")


@login_required
@user_passes_test(staff_required)
def revenue(request):
    return render(request, "dashboard/revenue.html")
