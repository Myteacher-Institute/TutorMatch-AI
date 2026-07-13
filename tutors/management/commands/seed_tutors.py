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
            self.stdout.write("  Updated existing tutor Trent Baakers to approved and assigned subjects.")

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully! All seeded users have password: password123"))

