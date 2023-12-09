from django.db import models

# Create your models here.

class Donor(models.Model):
    name = models.CharField(max_length=255)
    email_id = models.EmailField(unique=True)
    phone_no = models.CharField(max_length=15)
    home_address = models.TextField(blank=False, null=False)
    office_address = models.TextField(blank=True, null=True)
    pan_card_no = models.CharField(max_length=10, unique=True)
    # donor_photo = models.ImageField(upload_to='donor_photos/', blank=True, null=True)

    def __str__(self):
        return self.name
