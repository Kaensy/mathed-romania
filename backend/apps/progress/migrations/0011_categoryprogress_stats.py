from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('progress', '0010_dailytestsession_answers'),
    ]

    operations = [
        migrations.AddField(
            model_name='categoryprogress',
            name='total_attempts',
            field=models.PositiveIntegerField(default=0, help_text='Total practice attempts logged for this category. Denormalized for fast reads.'),
        ),
        migrations.AddField(
            model_name='categoryprogress',
            name='correct_attempts',
            field=models.PositiveIntegerField(default=0, help_text='Correct practice attempts logged for this category. Denormalized for fast reads.'),
        ),
        migrations.AddField(
            model_name='categoryprogress',
            name='last_attempted_at',
            field=models.DateTimeField(blank=True, help_text='Timestamp of the most recent practice attempt in this category.', null=True),
        ),
    ]
