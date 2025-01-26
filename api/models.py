
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission, BaseUserManager
from django.contrib.auth.hashers import make_password


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        # Hash the password before saving the user
        user = self.model(username=username, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        # print("coming here to hashed password")
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        # Create a superuser with hashed password
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, password, **extra_fields)


    
    
class Institution(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    email = models.EmailField(max_length=50)
    phone_no = models.CharField(max_length=15)
    # created_by = models.ForeignKey(DhaanaDonationUser, on_delete= models.SET_NULL, null = True, blank = True)
    created_date = models.DateTimeField(auto_now_add=True)
    # print("coming here to hashed")
    def __str__(self):
        return self.name
    
class Assets(models.Model):
    name= models.CharField(max_length=255)
    # quantity= models.IntegerField()
    description=models.TextField()
    creadted_on=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name
    
    
class InstitutionBranch(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=50,null=True,blank=True)
    phone_no = models.CharField(max_length=15)
    image= models.ImageField(upload_to='Institution_Branch/', null=True, blank=True)
    girl_child = models.IntegerField()
    boy_child = models.IntegerField()
    # assets = models.ManyToManyField(Assets)
    employee_no= models.IntegerField()
    created_date = models.DateField(auto_now_add=True)
    monthly_invoice_limit = models.IntegerField()
    def __str__(self):
        return str(self.name) + " for " +  str(self.institution.name) 
    
class InstitutionBranchAsset(models.Model):
    asset = models.ForeignKey(Assets, on_delete=models.CASCADE)
    institution_branch = models.ForeignKey(InstitutionBranch, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} {self.asset.name} at {self.institution_branch.name}"
    


class DhaanaDonationUsers(AbstractUser):
    # date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    institution = models.ForeignKey(Institution, on_delete=models.SET_NULL, null=True, blank=True)
    institutionBranch = models.ForeignKey(InstitutionBranch, on_delete=models.SET_NULL, null=True, blank=True)
    objects = CustomUserManager()
    def __str__(self):
        return self.username
    
    # groups = models.ManyToManyField(
    #     Group,
    #     verbose_name=('groups'),
    #     blank=True,
    #     help_text=(
    #         'The groups this user belongs to. A user will get all permissions '
    #         'granted to each of their groups.'
    #     ),
    #     related_name='dhaana_user_groups',  # Change 'dhaana_user_groups' to your preference
    #     related_query_name='user',
    # )
    # user_permissions = models.ManyToManyField(
    #     Permission,
    #     verbose_name=('user permissions'),
    #     blank=True,
    #     help_text=('Specific permissions for this user.'),
    #     related_name='dhaana_user_permissions',  # Change 'dhaana_user_permissions' to your preference
    #     related_query_name='user',
    # )


class PasswordReset(models.Model):
    user = models.ForeignKey(DhaanaDonationUsers, on_delete=models.CASCADE)
    token = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

class Donor(models.Model):
    name = models.CharField(max_length=255)
    email_id = models.EmailField(blank=True, null=True)
    phone_no = models.CharField(max_length=15)
    home_address = models.TextField(blank=False, null=False)
    office_address = models.TextField(blank=True, null=True)
    pan_card_no = models.CharField(max_length=10, unique=False,null=True,blank=True)
    adhaar_no = models.CharField(max_length=10, unique=False,null=True,blank=True)
    donor_photo = models.ImageField(upload_to='donor_photos/', blank=True, null=True)

    def __str__(self):
        return self.name
    
class Donation(models.Model):
    donation_receipt = models.CharField(max_length=255, null=True, blank=True)
    receipt_no = models.CharField(max_length=256,null=True,blank=True)
    date_receipt = models.DateField()
    received_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_in_words = models.CharField(max_length=255)
    
    towards_choices = [
        ('food', 'Food'),
        ('clothing', 'Clothing'),
        ('education', 'Education'),
        ('others', 'Others'),  # Add this option for others
    ]
    towards = models.CharField(max_length=20, choices=towards_choices)
    
    donor = models.ForeignKey(Donor, on_delete=models.DO_NOTHING)
    
    donation_form_choices = [
        ('goods', 'Goods'),
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
        ('online_transfer', 'Online Transfer'),
    ]
    donation_form = models.CharField(max_length=20, choices=donation_form_choices)
    
    product_name = models.CharField(max_length=255, null=True, blank=True)  # Increased max_length for more product names
    donation_quantity = models.IntegerField(null=True, blank=True)
    quantity_unit = models.CharField(max_length=10, null=True, blank=True)  # New field
    
    photo_upload1 = models.ImageField(upload_to='donation_photos/', null=True, blank=True)
    photo_upload2 = models.ImageField(upload_to='donation_photos/', null=True, blank=True)
    
    describe_towards = models.TextField(null=True, blank=True)  # New field
    transaction_details = models.TextField(null=True, blank=True)  # New field
    other_product_details = models.TextField(null=True, blank=True)  # New field
    
    pan_number = models.CharField(max_length=20, null=True, blank=True)
    
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, null=True, blank=True)
    institutionBranch = models.ForeignKey(InstitutionBranch, on_delete=models.CASCADE, null=True, blank=True)
    
    donation_number = models.IntegerField(null=True, blank=True)
    
    created_by = models.ForeignKey(DhaanaDonationUsers, on_delete=models.DO_NOTHING, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.received_amount) + " received from " +  str(self.donor.name) 
    
    
class InstitutionGalary(models.Model):
    institution = models.ForeignKey(Institution,on_delete = models.CASCADE, null = True, blank = True)
    image= models.ImageField(upload_to='Institution_Galary/', null=True, blank=True)
    title = models.CharField(max_length=255)
    created_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.title) + " for " +  str(self.institution.name) 
    
class FoodInventoryList(models.Model):
    order_no = models.CharField(max_length=50)
    items_details = models.TextField()
    
    quantity = models.PositiveIntegerField()
    quantity_Unit = models.CharField(max_length=50)
    last_month_balance = models.PositiveIntegerField()
    items_received_from_other_centers = models.PositiveIntegerField()
    items_from_donors = models.PositiveIntegerField()
    purchased_items = models.PositiveIntegerField()
    total = models.PositiveIntegerField()
    items_given_to_kitchen = models.PositiveIntegerField()
    items_sent_to_other_bases = models.PositiveIntegerField()
    balance_due = models.PositiveIntegerField()
    remarks = models.TextField()
    institutionBranch = models.ForeignKey(InstitutionBranch, on_delete = models.CASCADE, null = True, blank = True)
    created_by = models.ForeignKey(DhaanaDonationUsers,on_delete = models.DO_NOTHING, null = True, blank = True)
    created_date = models.DateTimeField(auto_now_add=True)
    month = models.CharField(max_length=10)

    def __str__(self):
        return f"Order No: {self.order_no}"