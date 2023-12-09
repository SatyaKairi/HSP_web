from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Donor
class UserSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = User
        fields = ['username', 'email']
        
        

class DonorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donor
        fields = '__all__'