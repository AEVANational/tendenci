# Generated by Django 3.2.12 on 2022-12-26 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_auto_20180928_1714'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='creator_username',
            field=models.CharField(max_length=150),
        ),
        migrations.AlterField(
            model_name='project',
            name='owner_username',
            field=models.CharField(max_length=150),
        ),
    ]