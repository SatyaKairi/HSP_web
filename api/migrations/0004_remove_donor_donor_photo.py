# Generated by Django 4.2.7 on 2023-12-03 21:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_donor_donor_photo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='donor',
            name='donor_photo',
        ),
    ]
