# Generated by Django 4.2.14 on 2024-09-13 13:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0007_job_header_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='type_of_work',
            field=models.CharField(blank=True, default='', max_length=10),
        ),
    ]
