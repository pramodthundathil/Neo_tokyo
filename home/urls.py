
from django.urls import path, include
from .import views

urlpatterns = [
    path("demodata",views.demodata, name="demodata"),
    path('user_registration/', views.user_registration, name='user_registration'),
    path('get_user_data/<int:pk>/', views.get_user_data, name='get_user_data'),
]

