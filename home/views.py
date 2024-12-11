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
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.shortcuts import get_object_or_404
from django.core.cache import cache
from rest_framework_simplejwt.tokens import RefreshToken
import random
from django.conf import settings
from django.core.mail import send_mail,EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site

# Create your views here.
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['id'] = user.id  # This should match 'id'
        token['first_name'] = user.first_name
        return token

    
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer






# google login 

from django.shortcuts import redirect
from social_django.utils import psa

@csrf_exempt
@psa('social:complete')
def google_login(request):
    google_auth_url = request.backend.auth_url()
    return redirect(google_auth_url)

# google registration 


#google login 

from django.dispatch import receiver
# from social_django.signals import social_auth_registered
from django.contrib.auth.models import User

def create_user(backend, user, response, *args, **kwargs):
    """
    Custom user creation pipeline.
    Called if the user does not exist during authentication.
    """
    if not user:
        user_data = {
            'email': response.get('email'),
            'first_name': response.get('given_name'),
            'last_name': response.get('family_name'),
        }
        return {
            'is_new': True,
            'user': User.objects.create_user(**user_data)
        }


from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from social_django.utils import load_strategy
from social_django.models import UserSocialAuth
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()

@api_view(['GET'])
def google_callback(request):
    strategy = load_strategy(request)
    auth_backend = 'google-oauth2'

    # Extract the authorization code from the query parameters
    code = request.GET.get('code')
    if not code:
        return Response({'error': 'Authorization code not provided.'}, status=400)

    # Exchange code for token
    try:
        backend = strategy.get_backend(auth_backend)
        user = backend.do_auth(code)

        if not user:
            return Response({'error': 'Authentication failed.'}, status=400)

        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        })
    except Exception as e:
        return Response({'error': str(e)}, status=400)



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
    try:
        user = CustomUser.objects.get(email=identifier) if '@' in identifier else CustomUser.objects.get(phone_number=identifier)
    except CustomUser.DoesNotExist:
        return Response(
            {'error': 'User does not exist.'},
            status=status.HTTP_404_NOT_FOUND
        )
    # Generate a 6-digit OTP
    otp = random.randint(100000, 999999)

    # Save OTP in cache for 5 minutes
    cache.set(f'otp_{identifier}', otp, timeout=300)  # 300 seconds = 5 minutes

    # Simulate sending OTP (replace with email/SMS service)
    print(f"OTP for {identifier}: {otp}")
    email = user.email
    current_site = get_current_site(request)
    mail_subject = 'OTP for Account LOGIN -  NEO TOKYO'
    path = "SignUp"
    message = render_to_string('emailbody_otp.html', {'user': user,
                                                        'domain': current_site.domain,
                                                        'path':path,
                                                        'token':otp,})

    email = EmailMessage(mail_subject, message, to=[email])
    email.content_subtype = "html"
    email.send(fail_silently=True)

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
    # Check if email or phone number exists
    email = request.data.get('email')
    phone_number = request.data.get('phone_number')

    if CustomUser.objects.filter(email=email).exists():
        return Response(
            {"detail": "A user with this email already exists."},
            status=status.HTTP_400_BAD_REQUEST
        )
    if CustomUser.objects.filter(phone_number=phone_number).exists():
        return Response(
            {"detail": "A user with this phone number already exists."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Proceed with serializer validation and saving
    serializer = CustomUserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "User registered successfully!"},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Get User Data by ID

from rest_framework.exceptions import AuthenticationFailed, PermissionDenied

import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_data(request, pk):
    try:
        # Ensure the authenticated user can only access their own data
        if request.user.id != int(pk):
            return Response(
                {"detail": "You do not have permission to access this user's data."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Fetch and return the user data
        user = get_object_or_404(CustomUser, id=pk)
        serializer = CustomUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {"detail": str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

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


