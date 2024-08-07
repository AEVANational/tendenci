# Generated by Django 4.2.13 on 2024-07-16 16:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('regions', '0003_auto_20200902_1545'),
    ]

    operations = [
        migrations.AddField(
            model_name='region',
            name='tax_label_2',
            field=models.CharField(blank=True, default='', max_length=6, verbose_name='Label for tax 2'),
        ),
        migrations.AddField(
            model_name='region',
            name='tax_rate',
            field=models.DecimalField(blank=True, decimal_places=5, default=0, help_text='Example: 0.0825 for 8.25%.', max_digits=6),
        ),
        migrations.AddField(
            model_name='region',
            name='tax_rate_2',
            field=models.DecimalField(blank=True, decimal_places=5, default=0, help_text='Example: 0.0825 for 8.25%.', max_digits=6),
        ),
    ]
