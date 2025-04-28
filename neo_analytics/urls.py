from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'customer-analytics', views.CustomerAnalyticsViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('insights/', views.CustomerInsightsView.as_view(), name='customer-insights'),
    path('order-timing/', views.OrderTimingAnalyticsView.as_view(), name='order-timing-analytics'),
    path('dashboard-summary/', views.DashboardSummaryView.as_view(), name='dashboard-summary'),
]