
from django.urls import path, include
from .import views, views_testing

urlpatterns = [
    
    path("demodata",views.demodata, name="demodata"),
    path('user_registration/', views.user_registration, name='user_registration'),
    path('get_user_data/<int:pk>/', views.get_user_data, name='get_user_data'),
    path('generate_otp/', views.generate_otp, name='generate_otp'),
    path('verify_otp_and_login/', views.verify_otp_and_login, name='verify_otp_and_login'),

    # path('auth/google/', views.google_login, name='google_login'),
    path('auth/google/callback/', views.google_callback, name='google_callback'),
    path("auth/google/", views.GoogleAuthView.as_view(), name="google_auth"),


    #testing

    path("",views_testing.signin,name="signin")
]