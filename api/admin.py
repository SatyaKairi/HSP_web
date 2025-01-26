from django.contrib import admin

# Register your models here.

from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponse
import csv



def download_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')

    response['Content-Disposition'] = 'attachment; filename="report.csv"'

    writer = csv.writer(response)

    headers = [field.verbose_name for field in modeladmin.model._meta.fields]
    writer.writerow(headers)

    for obj in queryset:
        data_row = [getattr(obj, field.name) for field in modeladmin.model._meta.fields]
        writer.writerow(data_row)

    return response

download_csv.short_description =  "Download Selected items as CSV"

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = DhaanaDonationUsers
    list_display = ('username', 'email', 'is_active',
                    'is_staff', 'is_superuser', 'last_login',)
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active',
         'is_superuser', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login', 'date_joined')}),
        ('Additional Details', {'fields': ('profile_picture','is_admin','institution','institutionBranch')})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active','profile_picture','is_admin','institution','institutionBranch')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    
    actions = [download_csv]

@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    actions = [download_csv]

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    actions = [download_csv]
    
admin.site.register(DhaanaDonationUsers,CustomUserAdmin)

@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    actions = [download_csv]
    
    
# FoodInventoryList
@admin.register(FoodInventoryList)
class FoodInventoryListonAdmin(admin.ModelAdmin):
    actions = [download_csv]
    
    
    
@admin.register(InstitutionBranch)
class InstitutionBranchAdmin(admin.ModelAdmin):
    actions = [download_csv]
    
@admin.register(InstitutionGalary)
class InstitutionGalaryAdmin(admin.ModelAdmin):
    actions = [download_csv]
    
admin.site.register(Assets)
class AssetsAdmin(admin.ModelAdmin):
    actions = [download_csv]
    
admin.site.register(PasswordReset)
class PasswordResetAdmin(admin.ModelAdmin):
    actions = [download_csv]
    
admin.site.register(InstitutionBranchAsset)
class InstitutionBranchAssetAdmin(admin.ModelAdmin):
    actions = [download_csv]