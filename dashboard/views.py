from accounts.models import UserProfile
from django.shortcuts import render
from django.apps import apps
from accounts.decorators import admin_required


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
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        return render(request, "contact.html", {"success": True, "name": name})
    return render(request, "contact.html")


@admin_required
def admin_dashboard(request):
    total_tutors = UserProfile.objects.filter(role=UserProfile.ROLE_TUTOR).count()
    total_students = UserProfile.objects.filter(role=UserProfile.ROLE_STUDENT).count()

    total_bookings = 0
    total_revenue = "0.00"

    try:
        Booking = apps.get_model("bookings", "Booking")
        total_bookings = Booking.objects.count()
    except (LookupError, AttributeError):
        pass

    try:
        Payment = apps.get_model("payments", "Payment")
        from django.db.models import Sum
        paid_amount = Payment.objects.filter(payment_status="paid").aggregate(Sum("amount"))["amount__sum"] or 0
        total_revenue = f"{float(paid_amount):,.2f}"
    except (LookupError, AttributeError, ValueError):
        pass

    metrics = {
        "total_tutors": total_tutors,
        "total_students": total_students,
        "total_bookings": total_bookings,
        "total_revenue": total_revenue,
    }
    return render(request, "dashboard/admin_dashboard.html", {"metrics": metrics})


@admin_required
def verifications(request):
    action = request.POST.get("action")
    profile_id = request.POST.get("profile_id")
    if request.method == "POST" and action and profile_id:
        try:
            profile = UserProfile.objects.get(pk=profile_id)
            if action == "approve":
                profile.is_verified = True
                profile.save()

                try:
                    Tutor = apps.get_model("tutors", "Tutor")
                    tutor_obj = Tutor.objects.filter(user=profile.user).first()
                    if tutor_obj:
                        tutor_obj.verification_status = "approved"
                        tutor_obj.save()
                except (LookupError, AttributeError):
                    pass

            elif action == "reject":
                profile.is_verified = False
                profile.save()

                try:
                    Tutor = apps.get_model("tutors", "Tutor")
                    tutor_obj = Tutor.objects.filter(user=profile.user).first()
                    if tutor_obj:
                        tutor_obj.verification_status = "rejected"
                        tutor_obj.save()
                except (LookupError, AttributeError):
                    pass
        except UserProfile.DoesNotExist:
            pass

    pending_tutors = UserProfile.objects.filter(role=UserProfile.ROLE_TUTOR, is_verified=False).order_by("-created_at")
    return render(request, "dashboard/verifications.html", {"pending_tutors": pending_tutors})


@admin_required
def users(request):
    action = request.POST.get("action")
    user_id = request.POST.get("user_id")
    if request.method == "POST" and action and user_id:
        try:
            profile = UserProfile.objects.get(pk=user_id)
            if action == "toggle_verify":
                profile.is_verified = not profile.is_verified
                profile.save()
            elif action == "delete":
                profile.user.delete()
        except UserProfile.DoesNotExist:
            pass

    user_list = UserProfile.objects.all().order_by("-created_at")
    return render(request, "dashboard/users.html", {"user_list": user_list})


@admin_required
def bookings(request):
    return render(request, "dashboard/bookings.html")


@admin_required
def revenue(request):
    return render(request, "dashboard/revenue.html")
