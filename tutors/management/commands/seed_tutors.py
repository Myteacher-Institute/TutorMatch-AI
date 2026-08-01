import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile
from tutors.models import Tutor, Subject

class Command(BaseCommand):
    help = "Seeds the database with subjects and approved Port Harcourt tutors for testing"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding subjects...")
        subject_names = [
            "Mathematics",
            "English",
            "Physics",
            "Chemistry",
            "Biology",
            "Economics",
            "HTML",
            "Coding",
            "Programming",
        ]
        subjects = {}
        for name in subject_names:
            sub, created = Subject.objects.get_or_create(subject_name=name)
            subjects[name] = sub
            if created:
                self.stdout.write(f"  Created subject: {name}")

        self.stdout.write("Seeding users and profiles...")
        users_to_seed = [
            {
                "username": "student1@example.com",
                "email": "student1@example.com",
                "first_name": "Tobi",
                "last_name": "Alabi",
                "role": UserProfile.ROLE_STUDENT,
                "is_verified": True,
            },
            {
                "username": "student2@example.com",
                "email": "student2@example.com",
                "first_name": "Chioma",
                "last_name": "Eke",
                "role": UserProfile.ROLE_STUDENT,
                "is_verified": True,
            },
            {
                "username": "tutor1@example.com",
                "email": "tutor1@example.com",
                "first_name": "Ngozi",
                "last_name": "Nwosu",
                "role": UserProfile.ROLE_TUTOR,
                "is_verified": True,
            },
            {
                "username": "tutor2@example.com",
                "email": "tutor2@example.com",
                "first_name": "Amaka",
                "last_name": "Chidi",
                "role": UserProfile.ROLE_TUTOR,
                "is_verified": True,
            },
            {
                "username": "tutor3@example.com",
                "email": "tutor3@example.com",
                "first_name": "Blessing",
                "last_name": "Peters",
                "role": UserProfile.ROLE_TUTOR,
                "is_verified": True,
            },
            {
                "username": "admin1@example.com",
                "email": "admin1@example.com",
                "first_name": "Marketplace",
                "last_name": "Admin",
                "role": UserProfile.ROLE_ADMIN,
                "is_verified": True,
                "is_staff": True,
                "is_superuser": True,
            },
        ]

        user_profiles = {}
        for u_data in users_to_seed:
            user = User.objects.filter(username=u_data["username"]).first()
            if not user:
                user = User.objects.create_user(
                    username=u_data["username"],
                    email=u_data["email"],
                    password="password123",
                    first_name=u_data["first_name"],
                    last_name=u_data["last_name"],
                )
                self.stdout.write(f"  Created user: {u_data['username']}")
            
            if u_data.get("is_staff") or u_data.get("is_superuser"):
                user.is_staff = u_data.get("is_staff", False)
                user.is_superuser = u_data.get("is_superuser", False)
                user.save()

            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.role = u_data["role"]
            profile.is_verified = u_data["is_verified"]
            profile.save()
            user_profiles[u_data["username"]] = profile

        self.stdout.write("Seeding tutor profiles...")
        tutors_to_seed = [
            {
                "profile_email": "tutor1@example.com",
                "bio": "Specializes in SS3 Mathematics, has extensive WAEC preparation experience with a 95% pass rate, teaches weekends, and is located just 1.2km from GRA Port Harcourt.",
                "location": "GRA",
                "rate_amount": 7500,
                "years_experience": 8,
                "verification_status": "approved",
                "subjects": ["Mathematics", "Physics"],
            },
            {
                "profile_email": "tutor2@example.com",
                "bio": "Dedicated Mathematics and Chemistry tutor with a passion for helping high schoolers succeed.",
                "location": "Rumuola",
                "rate_amount": 5000,
                "years_experience": 5,
                "verification_status": "approved",
                "subjects": ["Mathematics", "Chemistry"],
            },
            {
                "profile_email": "tutor3@example.com",
                "bio": "Energetic B.Sc Mathematics graduate focusing on building fundamental problem-solving skills.",
                "location": "Trans Amadi",
                "rate_amount": 4500,
                "years_experience": 3,
                "verification_status": "approved",
                "subjects": ["Mathematics"],
            },
        ]

        for t_data in tutors_to_seed:
            profile = user_profiles.get(t_data["profile_email"])
            if not profile:
                continue

            tutor, created = Tutor.objects.get_or_create(user=profile)
            tutor.bio = t_data["bio"]
            tutor.location = t_data["location"]
            tutor.rate_amount = t_data["rate_amount"]
            tutor.years_experience = t_data["years_experience"]
            tutor.verification_status = t_data["verification_status"]
            tutor.save()

            # Assign subjects
            sub_objs = [subjects[s_name] for s_name in t_data["subjects"] if s_name in subjects]
            tutor.subjects.set(sub_objs)
            self.stdout.write(f"  Configured tutor: {profile.user.get_full_name()} ({t_data['location']})")

        # Also verify the existing Trent Baakers tutor if exists
        trent = Tutor.objects.filter(user__user__username="TB@gmail.com").first()
        if trent:
            trent.verification_status = "approved"
            trent.location = "GRA"
            trent.rate_amount = 8000
            trent.years_experience = 4
            trent.save()
            trent.subjects.set([subjects["English"], subjects["Economics"]])
            trent.user.is_verified = True
            trent.user.save()
        # Seed Course Offers
        self.stdout.write("Seeding Course Offers...")
        from tutors.models import CourseOffer

        courses_to_seed = [
            {
                "tutor_email": "tutor1@example.com",
                "title": "Python Programming for Absolute Beginners (3 Months)",
                "subject_name": "Coding",
                "cover_image": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=800&q=80",
                "daily_rate": 3500,
                "days_per_week": 2,
                "duration_months": 3,
                "currency": "NGN",
                "delivery_mode": "online",
                "online_platform": "google_meet",
                "schedule_days_times": "Mondays & Wednesdays, 4:00 PM - 6:00 PM (WAT)",
                "description": "Comprehensive 3-month course covering Python syntax, data structures, object-oriented programming, and building real-world automation scripts.",
                "rules": "1. 80% attendance required for completion certificate.\n2. Assignments must be submitted before Sunday midnight.",
                "requirements": "Laptop with Windows 10/11 or macOS, internet connection, VS Code installed.",
            },
            {
                "tutor_email": "tutor2@example.com",
                "title": "WAEC & JAMB Mathematics Intensive (2 Months)",
                "subject_name": "Mathematics",
                "cover_image": "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?auto=format&fit=crop&w=800&q=80",
                "daily_rate": 2500,
                "days_per_week": 3,
                "duration_months": 2,
                "currency": "NGN",
                "delivery_mode": "home",
                "physical_location": "Student Home Location (Port Harcourt & Environs)",
                "schedule_days_times": "Tuesdays, Thursdays & Saturdays, 5:00 PM - 7:00 PM",
                "description": "Master essential WAEC & JAMB mathematics topics including Algebra, Trigonometry, Calculus, and past question walkthroughs with a proven 95%+ pass rate.",
                "rules": "1. Punctuality is essential.\n2. Formula notebook required for all sessions.",
                "requirements": "WAEC/JAMB past questions book, scientific calculator, exercise book.",
            },
            {
                "tutor_email": "tutor3@example.com",
                "title": "C++ Systems & Game Algorithm Foundations (1 Month)",
                "subject_name": "Programming",
                "cover_image": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=800&q=80",
                "daily_rate": 4000,
                "days_per_week": 2,
                "duration_months": 1,
                "currency": "NGN",
                "delivery_mode": "online",
                "online_platform": "zoom",
                "schedule_days_times": "Saturdays & Sundays, 2:00 PM - 4:00 PM",
                "description": "Learn low-level memory management, pointers, object-oriented principles, and algorithm design using modern C++20.",
                "rules": "1. Active participation during coding exercises.\n2. Respectful communication in chat.",
                "requirements": "PC with GCC / Clang / MSVC compiler installed.",
            },
            {
                "tutor_email": "tutor1@example.com",
                "title": "Modern Web Development: HTML, CSS & JavaScript (2 Months)",
                "subject_name": "HTML",
                "cover_image": "https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?auto=format&fit=crop&w=800&q=80",
                "daily_rate": 3000,
                "days_per_week": 2,
                "duration_months": 2,
                "currency": "NGN",
                "delivery_mode": "online",
                "online_platform": "google_meet",
                "schedule_days_times": "Tuesdays & Thursdays, 6:00 PM - 8:00 PM",
                "description": "Build modern, responsive websites from scratch using HTML5, CSS3, Flexbox, Grid, and interactive JavaScript.",
                "rules": "1. Weekly project submissions.",
                "requirements": "Computer with Chrome browser & VS Code.",
            },
        ]

        for c_data in courses_to_seed:
            t_profile = user_profiles.get(c_data["tutor_email"])
            if not t_profile or not hasattr(t_profile, "tutor_profile"):
                continue
            tutor = t_profile.tutor_profile
            sub = subjects.get(c_data["subject_name"])

            offer, created = CourseOffer.objects.get_or_create(
                tutor=tutor,
                title=c_data["title"],
                defaults={
                    "subject": sub,
                    "cover_image": c_data["cover_image"],
                    "daily_rate": c_data["daily_rate"],
                    "days_per_week": c_data["days_per_week"],
                    "duration_months": c_data["duration_months"],
                    "currency": c_data["currency"],
                    "delivery_mode": c_data["delivery_mode"],
                    "online_platform": c_data.get("online_platform", "google_meet"),
                    "physical_location": c_data.get("physical_location", ""),
                    "schedule_days_times": c_data["schedule_days_times"],
                    "description": c_data["description"],
                    "rules": c_data.get("rules", ""),
                    "requirements": c_data.get("requirements", ""),
                    "is_active": True,
                }
            )
            if created:
                self.stdout.write(f"  Created course offer: {offer.title}")

        # Seed initial success stories if empty
        from accounts.models import SuccessStory
        if SuccessStory.objects.count() == 0:
            user = User.objects.filter(is_superuser=True).first() or User.objects.first()
            if user:
                initial_stories = [
                    {
                        "title": "JAMB Score Improvement",
                        "story": "My son's JAMB score improved from 210 to 290 thanks to the amazing tutor we found here. The AI matching really worked for us!",
                        "rating": 5,
                    },
                    {
                        "title": "Steady Stream of Serious Students",
                        "story": "As a tutor, this platform has provided me with a steady stream of serious students. The payment system is incredibly transparent.",
                        "rating": 5,
                    },
                    {
                        "title": "Exceptional Coding Tutor for Kids",
                        "story": "The coding tutor we found for our kids was exceptional. They went from zero knowledge to building basic websites in months.",
                        "rating": 5,
                    },
                ]
                for s in initial_stories:
                    SuccessStory.objects.create(
                        user=user,
                        title=s["title"],
                        story=s["story"],
                        rating=s["rating"],
                    )
                self.stdout.write("  Created initial success stories.")

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully! All seeded users have password: password123"))

