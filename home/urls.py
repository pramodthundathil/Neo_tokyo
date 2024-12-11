
from django.urls import path, include
from .import views

urlpatterns = [
    path("demodata",views.demodata, name="demodata"),
    path('user_registration/', views.user_registration, name='user_registration'),
    path('get_user_data/<int:pk>/', views.get_user_data, name='get_user_data'),
    path('generate_otp/', views.generate_otp, name='generate_otp'),
    path('verify_otp_and_login/', views.verify_otp_and_login, name='verify_otp_and_login'),
]



