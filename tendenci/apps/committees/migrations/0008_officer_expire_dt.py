# Generated by Django 2.2.24 on 2021-06-06 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('committees', '0007_auto_20210525_1250'),
    ]

    operations = [
        migrations.AddField(
            model_name='officer',
            name='expire_dt',
            field=models.DateField(blank=True, null=True, verbose_name='Expire Date', help_text='Leave it blank if never expires.')
        ),
    ]