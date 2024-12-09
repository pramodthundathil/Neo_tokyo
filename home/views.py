from django.shortcuts import render, redirect, get_object_or_404
import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomUserSerializer
from .models import CustomUser

# Create your views here.
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['id'] = user.id
        token['first_name'] = user.first_name
        return token
    
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer



@permission_classes([IsAuthenticated])
@csrf_exempt
@api_view(["GET"])
def demodata(request):
    data = {
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number":"+12345678901",
    "date_of_birth": "1990-01-01",
    "pin_code": 123456,
    "village": "Sample Village",
    "district": "Sample District",
    "state": "Sample State",
    "address": "123 Sample Street",
    "role": "user",
    "password": "securepassword"
    }


    return Response(data)



# User Creation from api User model CustomUser serializer from home.serializer.py CustomUserSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def user_registration(request):
    if request.method == 'POST':
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User registered successfully!"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


@permission_classes([IsAuthenticated])
@csrf_exempt
@api_view(["GET"])
def get_user_data(request,pk):
    user = get_object_or_404(CustomUser, id = pk)
    user_serializer = CustomUserSerializer(user, many = False)
    data = user_serializer.data
    return Response(data)
