from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token  # Import the view

from .views import *




urlpatterns = [
    path('user/login/', UserLoginAPIView.as_view(), name='user-login'),
    path('donors/create/', DonorCreateView.as_view(), name='donor-create'),
]
