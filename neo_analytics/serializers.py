from rest_framework import serializers
from .models import CustomerAnalytics, AgeGroupMetrics, OrderTimingAnalytics, DailyAnalyticsSnapshot
from home.models import CustomUser
from orders.models import Order

class CustomerAnalyticsSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    days_since_last_order = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomerAnalytics
        fields = [
            'id', 'user_email', 'user_name', 'total_orders', 'total_spent',
            'average_order_value', 'first_purchase_date', 'last_purchase_date',
            'purchase_frequency_days', 'return_rate', 'is_active',
            'preferred_payment_method', 'days_since_last_order'
        ]
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() if obj.user.first_name else obj.user.email
    
    def get_days_since_last_order(self, obj):
        if not obj.last_purchase_date:
            return None
        from django.utils import timezone
        return (timezone.now() - obj.last_purchase_date).days

class AgeGroupMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgeGroupMetrics
        fields = '__all__'

class OrderTimingAnalyticsSerializer(serializers.ModelSerializer):
    day_name = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderTimingAnalytics
        fields = ['date', 'hour_of_day', 'day_of_week', 'day_name', 'order_count', 'total_revenue']
    
    def get_day_name(self, obj):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return days[obj.day_of_week]

class DailyAnalyticsSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyAnalyticsSnapshot
        fields = '__all__'

class CustomerInsightsSerializer(serializers.Serializer):
    """Comprehensive customer insights serializer"""
    average_order_value = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    active_customers_count = serializers.IntegerField(read_only=True)
    inactive_customers_count = serializers.IntegerField(read_only=True)
    most_loyal_customers = serializers.ListField(child=serializers.DictField(), read_only=True)
    top_customers_by_revenue = serializers.ListField(child=serializers.DictField(), read_only=True)
    least_spending_customers = serializers.ListField(child=serializers.DictField(), read_only=True)
    average_purchase_frequency = serializers.FloatField(read_only=True)
    customer_churn_rate = serializers.FloatField(read_only=True)
    gender_analysis = serializers.DictField(read_only=True)
    age_group_analysis = serializers.ListField(child=serializers.DictField(), read_only=True)
    preferred_payment_methods = serializers.DictField(read_only=True)
    return_rate = serializers.FloatField(read_only=True)