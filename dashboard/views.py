from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render


def home(request):
    featured_tutors = [
        {
            "id": 1,
            "name": "Dr. Samuel Adebayo",
            "title": "MSc. Applied Mathematics",
            "rate": "5k",
            "rating": "4.9",
            "tags": ["Mathematics", "Physics", "JAMB/WAEC"],
            "photo": "https://images.unsplash.com/photo-1560250097-0b93528c311a?auto=format&fit=crop&w=700&q=80",
        },
        {
            "id": 2,
            "name": "Sarah Johnson",
            "title": "IELTS/TOEFL Expert",
            "rate": "4.5k",
            "rating": "5.0",
            "tags": ["English", "Literature", "Diction"],
            "photo": "https://images.unsplash.com/photo-1580894732444-8ecded7900cd?auto=format&fit=crop&w=700&q=80",
        },
        {
            "id": 3,
            "name": "Chidi Okoro",
            "title": "Senior Software Engineer",
            "rate": "8k",
            "rating": "4.8",
            "tags": ["Python", "Web Dev", "Scratch"],
            "photo": "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=700&q=80",
        },
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
