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



from django.shortcuts import get_object_or_404
from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomUserSerializer
from .models import CustomUser
import random


# OTP Generation
@api_view(['POST'])
@permission_classes([AllowAny])
def generate_otp(request):
    identifier = request.data.get('identifier')  # Email or phone number
    if not identifier:
        return Response(
            {'error': 'Email or phone number is required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Generate a 6-digit OTP
    otp = random.randint(100000, 999999)

    # Save OTP in cache for 5 minutes
    cache.set(f'otp_{identifier}', otp, timeout=300)  # 300 seconds = 5 minutes

    # Simulate sending OTP (replace with email/SMS service)
    print(f"OTP for {identifier}: {otp}")

    return Response(
        {'message': 'OTP sent successfully.'},
        status=status.HTTP_200_OK
    )


# OTP Verification and Token Issuance
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp_and_login(request):
    identifier = request.data.get('identifier')
    otp = request.data.get('otp')

    if not identifier or not otp:
        return Response(
            {'error': 'Identifier and OTP are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Retrieve OTP from cache
    stored_otp = cache.get(f'otp_{identifier}')
    if stored_otp is None or str(stored_otp) != str(otp):
        return Response(
            {'error': 'Invalid or expired OTP.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check if user exists
    try:
        user = CustomUser.objects.get(email=identifier) if '@' in identifier else CustomUser.objects.get(phone_number=identifier)
    except CustomUser.DoesNotExist:
        return Response(
            {'error': 'User does not exist.'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Generate JWT tokens
    print(user,"-----------------")
    refresh = RefreshToken.for_user(user)
    access = refresh.access_token

    # Remove OTP from cache after successful verification
    cache.delete(f'otp_{identifier}')

    return Response(
        {
            'refresh': str(refresh),
            'access': str(access),
            'message': 'Login successful.'
        },
        status=status.HTTP_200_OK
    )



# User Creation from api User model CustomUser serializer from home.serializer.py CustomUserSerializer


# User Registration
@api_view(['POST'])
@permission_classes([AllowAny])
def user_registration(request):
    serializer = CustomUserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "User registered successfully!"},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





# Get User Data by ID
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_data(request, pk):
    user = get_object_or_404(CustomUser, id=pk)
    serializer = CustomUserSerializer(user)
    return Response(serializer.data)



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


