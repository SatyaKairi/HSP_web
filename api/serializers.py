from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *

class PasswordResetSerializer(serializers.ModelSerializer):
    class Meta:
        model = PasswordReset
        fields = ['user', 'token', 'timestamp']

class UserSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(source='institution.name', read_only=True)
    class Meta:
        model = DhaanaDonationUsers
        fields = ['username', 'email','is_admin','profile_picture','institution','institution_name']
        
class FoodInventoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodInventoryList
        fields = '__all__'

class DonorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donor
        fields = ['order_no','items_details','quantity','quantity_Unit','last_month_balance','items_received_from_other_centers','items_from_donors',
                  'purchased_items','total','items_given_to_kitchen','items_sent_to_other_bases','balance_due','remarks','institutionBranch','month'
                  
                  ]
    def get_queryset(self):
        fields = self.Meta.fields
        return FoodInventoryList.objects.values(*fields)
        
        
class DonationSerializer(serializers.ModelSerializer):
    donor_name = serializers.CharField(source='donor.name', read_only=True)
    class Meta:
        model = Donation
        fields = '__all__'
        
class InstitutionGalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = InstitutionGalary
        fields = ['image', 'title']
        
        
class DonorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donor
        fields = '__all__'
        
class InstitutionBranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstitutionBranch
        fields = ['id', 'name', 'image', 'girl_child', 'boy_child', 'employee_no', 'created_date']
        
        
        
# for branch detail view

class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assets
        fields = ['name']

class InstitutionBranchAssetSerializer(serializers.ModelSerializer):
    asset = serializers.CharField(source='asset.name')
    class Meta:
        model = InstitutionBranchAsset
        fields = ['asset', 'quantity']

class BranchDetailSerializer(serializers.ModelSerializer):
    assets = InstitutionBranchAssetSerializer(many=True, read_only=True)

    class Meta:
        model = InstitutionBranch
        fields = ['id', 'name', 'assets', 'girl_child', 'boy_child', 'employee_no', 'created_date']

class BranchStatsSerializer(serializers.Serializer):
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_goods_donations = serializers.IntegerField(read_only=True)
    total_donation = serializers.IntegerField(read_only=True)