# Generated by Django 4.2.7 on 2024-09-08 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0023_donation_receipt_no'),
    ]

    operations = [
        migrations.AddField(
            model_name='institutionbranch',
            name='monthly_invoice_limit',
            field=models.IntegerField(default=5),
            preserve_default=False,
        ),
    ]
