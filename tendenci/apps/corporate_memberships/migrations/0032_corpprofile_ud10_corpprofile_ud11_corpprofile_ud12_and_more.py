# Generated by Django 4.2.20 on 2025-05-06 21:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corporate_memberships', '0031_notice_region_notice_regions_to_exclude_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='corpprofile',
            name='ud10',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AddField(
            model_name='corpprofile',
            name='ud11',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AddField(
            model_name='corpprofile',
            name='ud12',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AddField(
            model_name='corpprofile',
            name='ud13',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AddField(
            model_name='corpprofile',
            name='ud14',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AddField(
            model_name='corpprofile',
            name='ud15',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AddField(
            model_name='corpprofile',
            name='ud16',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AddField(
            model_name='corpprofile',
            name='ud17',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AddField(
            model_name='corpprofile',
            name='ud18',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AddField(
            model_name='corpprofile',
            name='ud9',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]
