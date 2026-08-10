from django.db import migrations


def update_blog_images_and_authors(apps, schema_editor):
    BlogPost = apps.get_model("blog", "BlogPost")

    img_map = {
        "how-to-score-300-in-jamb-utme-and-ace-waec": "/static/images/blog/jamb-cbt-center.png",
        "advantages-of-hiring-verified-home-tutor-nigeria": "/static/images/blog/tutor-reading-with-children.png",
        "how-ai-matching-is-revolutionizing-private-education-nigeria": "/static/images/blog/african-students-study-group.png",
    }

    for slug, image_url in img_map.items():
        BlogPost.objects.filter(slug=slug).update(image_url=image_url)


def reverse_update(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0002_seed_initial_blog_posts"),
    ]

    operations = [
        migrations.RunPython(update_blog_images_and_authors, reverse_update),
    ]
