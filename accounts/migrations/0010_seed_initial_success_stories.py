from django.db import migrations


def seed_initial_stories(apps, schema_editor):
    User = apps.get_model("auth", "User")
    SuccessStory = apps.get_model("accounts", "SuccessStory")

    if SuccessStory.objects.count() == 0:
        admin_user = User.objects.filter(is_superuser=True).first() or User.objects.first()
        if not admin_user:
            admin_user = User.objects.create_user(
                username="system_community",
                email="community@myteacherconnect.org",
                first_name="Community",
                last_name="Member"
            )

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
                user=admin_user,
                title=s["title"],
                story=s["story"],
                rating=s["rating"],
            )


def reverse_seed(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_homepagestatssetting_video_section_active_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_initial_stories, reverse_code=reverse_seed),
    ]
