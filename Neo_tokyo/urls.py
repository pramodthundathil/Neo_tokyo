
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from home import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path("authentication/",include("home.urls")),
    path("inventory/",include("inventory.urls"))

]


urlpatterns += [
    path('api/token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]