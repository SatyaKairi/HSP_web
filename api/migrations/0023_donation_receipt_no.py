# Generated by Django 4.2.7 on 2024-09-08 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0022_alter_dhaanadonationusers_groups_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='receipt_no',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
