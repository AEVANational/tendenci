# Generated by Django 3.2.23 on 2024-12-09 13:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0007_auto_20200902_1545'),
        ('studygroups', '0004_auto_20200902_1545'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studygroup',
            name='header_image',
            field=models.ForeignKey(default=None, help_text='Only jpg, gif, or png images.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='studiygroups', to='files.file'),
        ),
    ]
