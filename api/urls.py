from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token  # Import the view

from .views import *




urlpatterns = [
    path('user/login/', UserLoginAPIView.as_view(), name='user-login'),
    path('donors/create/', DonorCreateView.as_view(), name='donor-create'),
    path('donations/', DonationAPIView.as_view(), name='donation-api'),
    path('donations/list/', DonationViewSet.as_view({'get': 'list'}), name='donation'), 
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/<str:token>/', ResetPasswordView.as_view(), name='reset-password'),
    path('institution-galary/<int:institution_id>/', InstitutionGalaryAPIView.as_view(), name='institution-galary-api'),
    path('donor/', DonorDetailsAPIView.as_view(), name='donor-details'),
    path('branches/<int:institution_id>/', BranchListAPIView.as_view(), name='api-branch-list'),
    path('branch/<int:branch_id>/', BranchDetailView.as_view(), name='branch-detail'),
    path('privacy-policy/', privacy_policy, name='privacy_policy'),
    path('donation-details/<int:pk>/', DonationDetailsAPIView.as_view(), name='donation-details'),
    
    # FoodInventoryListAPIView
    path('foodinventorylist/', FoodInventoryListAPIView.as_view(), name='food_inventory_list'),
]
