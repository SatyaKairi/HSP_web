# Generated by Django 4.2.7 on 2024-08-19 02:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0020_donation_describe_towards_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='institutionbranch',
            name='email',
            field=models.EmailField(default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='institutionbranch',
            name='phone_no',
            field=models.IntegerField(default=12221),
            preserve_default=False,
        ),
    ]
