from django.shortcuts import render
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .serializers import *
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated,AllowAny 
from rest_framework import status
from typing import Any
from django.contrib.auth.base_user import AbstractBaseUser
from rest_framework.decorators import action, api_view, permission_classes


# def authenticate(request: Any = ..., **credentials: Any) -> AbstractBaseUser | None: ...


# Create your views here.

class UserLoginAPIView(APIView):
    print("Coming here")
    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        print(username, password)
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            serializer = UserSerializer(user)
            context={
                "token": token.key,
                "user" : serializer.data
                
            }
            return Response(context, status=status.HTTP_200_OK)
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
    

@permission_classes([IsAuthenticated])
class DonorCreateView(generics.CreateAPIView):
    queryset = Donor.objects.all()
    serializer_class = DonorSerializer