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


from social_django.utils import load_strategy
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model


from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action


from .models import DeliveryAddress
from .serializers import DeliveryAddressSerializer

#swagger authentication

from rest_framework.permissions import BasePermission

class IsAuthenticatedForSwagger(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

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


from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    Custom permission to only allow admin users to access this view.
    """
    def has_permission(self, request, view):
        # Check if the user is authenticated and has the 'admin' role
        return request.user and request.user.role == 'admin'



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




# Google Authentication callback class 
from google.auth.transport import requests
from google.oauth2 import id_token

User = get_user_model()

class GoogleAuthView(APIView):
    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verify token with Google
            google_info = id_token.verify_oauth2_token(token, requests.Request())

            if 'email' not in google_info:
                return Response({"error": "Invalid Google token"}, status=status.HTTP_400_BAD_REQUEST)

            email = google_info["email"]
            google_id = google_info["sub"]
            name = google_info.get("name", "")
            profile_picture = google_info.get("picture", "")

            user, created = User.objects.get_or_create(email=email, defaults={
                "email": email,
                'first_name':name,
                "google_id": google_id,
                "profile_picture": profile_picture,
                "is_google_authenticated": True,
            })

            if not created:
                user.google_id = google_id
                user.profile_picture = profile_picture
                user.is_google_authenticated = True
                user.save()

            # Generate JWT token
            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.username,
                    "profile_picture": user.profile_picture
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


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

    # Simulate sending OTP 
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

    is_admin = user.is_superuser,
    role = user.role
    # Remove OTP from cache after successful verification
    cache.delete(f'otp_{identifier}')
    print({
            'refresh': str(refresh),
            'access': str(access),
            'message': 'Token Creation successful.',
            'is_admin':is_admin,
            "role":role
        })

    return Response(
        {
            'refresh': str(refresh),
            'access': str(access),
            'message': 'Token Creation successful.',
            'is_admin':is_admin[0],
            "role":role
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


class DeliveryAddressViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing delivery addresses for authenticated users.
    """
    serializer_class = DeliveryAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return only addresses belonging to the current user"""
        print("Get Current User...................")
        try:
            return DeliveryAddress.objects.filter(user=self.request.user)
        except Exception as e:
            return DeliveryAddress.objects.none()
            

    def perform_create(self, serializer):
        """Automatically assign the current user when creating an address"""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def primary(self, request):
        """Get the user's primary delivery address"""
        primary_address = self.get_queryset().filter(is_primary=True).first()
        if primary_address:
            serializer = self.get_serializer(primary_address)
            return Response(serializer.data)
        return Response({"detail": "No primary address found."}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def set_primary(self, request, pk=None):
        """Set an address as the primary delivery address"""
        address = self.get_object()
        address.is_primary = True
        address.save()  # The save method will handle updating other addresses
        serializer = self.get_serializer(address)
        return Response(serializer.data)