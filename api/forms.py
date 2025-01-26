# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import *

class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput, label='New Password')
    confirm_password = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')
    
    
class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = DhaanaDonationUsers
        fields = ('email',)

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = DhaanaDonationUsers
        fields = ('email',)
