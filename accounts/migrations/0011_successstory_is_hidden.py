# Generated manually for is_hidden field on SuccessStory
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_seed_initial_success_stories'),
    ]

    operations = [
        migrations.AddField(
            model_name='successstory',
            name='is_hidden',
            field=models.BooleanField(default=False, help_text='Hide story from public view'),
        ),
    ]
