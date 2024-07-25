# Generated by Django 4.2.13 on 2024-07-21 17:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('regions', '0005_region_invoice_footer_region_invoice_header'),
        ('invoices', '0010_invoice_tax_2_invoice_tax_label_2_invoice_tax_rate_2'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='regions.region'),
        ),
    ]
