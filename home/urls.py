
from django.urls import path, include
from .import views, views_testing
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
urlpatterns = [
    
    path("demodata",views.demodata, name="demodata"),
    path('user_registration/', views.user_registration, name='user_registration'),
    path('get_user_data/<int:pk>/', views.get_user_data, name='get_user_data'),
    path('generate_otp/', views.generate_otp, name='generate_otp'),
    path('register/verify-otp/', views.verify_registration_otp, name='verify_registration_otp'),
    path('register/resend-otp/', views.resend_registration_otp, name='resend_registration_otp'),

    path('verify_otp_and_login/', views.verify_otp_and_login, name='verify_otp_and_login'),

    # path('auth/google/', views.google_login, name='google_login'),
    path('auth/google/callback/', views.google_callback, name='google_callback'),
    path("auth/google/", views.GoogleAuthView.as_view(), name="google_auth"),


    #testing

    path("",views_testing.signin,name="signin")
]

router.register(r'delivery-addresses', views.DeliveryAddressViewSet, basename='delivery-address')
urlpatterns +=router.urls

