from django.db import models
from django.utils import timezone
from home.models import CustomUser
from orders.models import Order, OrderItem
from datetime import timedelta
from django.db.models import Sum, Count, Avg, F, Q

class CustomerAnalytics(models.Model):
    """Store computed analytics for each customer"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='analytics')
    total_orders = models.IntegerField(default=0)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    first_purchase_date = models.DateTimeField(null=True, blank=True)
    last_purchase_date = models.DateTimeField(null=True, blank=True)
    purchase_frequency_days = models.FloatField(default=0)  # Average days between orders
    return_rate = models.FloatField(default=0)  # Percentage of returned items
    is_active = models.BooleanField(default=True)  # Active within last 3 months
    preferred_payment_method = models.CharField(max_length=50, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Analytics for {self.user.email}"

    @classmethod
    def update_for_user(cls, user):
        """Update analytics for a specific user"""
        analytics, created = cls.objects.get_or_create(user=user)
        
        # Get user orders
        orders = Order.objects.filter(user=user).order_by('created_at')
        completed_orders = orders.filter(order_status='PAID')
        
        analytics.total_orders = completed_orders.count()
        analytics.total_spent = completed_orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
        
        if analytics.total_orders > 0:
            analytics.average_order_value = analytics.total_spent / analytics.total_orders
            analytics.first_purchase_date = orders.first().created_at if orders.exists() else None
            analytics.last_purchase_date = orders.last().created_at if orders.exists() else None
            
            # Calculate purchase frequency (if more than one order)
            if analytics.total_orders > 1 and analytics.first_purchase_date and analytics.last_purchase_date:
                days_diff = (analytics.last_purchase_date - analytics.first_purchase_date).days
                analytics.purchase_frequency_days = days_diff / (analytics.total_orders - 1) if days_diff > 0 else 0
            
            # Check if active (purchased within last 90 days)
            analytics.is_active = analytics.last_purchase_date > (timezone.now() - timedelta(days=90)) if analytics.last_purchase_date else False
            
            # Most used payment method (placeholder - update based on your payment data)
            payment_methods = completed_orders.values('payment_order_id').annotate(count=Count('id')).order_by('-count')
            if payment_methods.exists():
                analytics.preferred_payment_method = payment_methods.first()['payment_order_id']
        
        analytics.save()
        return analytics

class AgeGroupMetrics(models.Model):
    """Metrics aggregated by age groups"""
    age_group = models.CharField(max_length=20)  # e.g. "18-24", "25-34"
    total_customers = models.IntegerField(default=0)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    most_popular_product_id = models.IntegerField(null=True, blank=True)
    most_popular_product_name = models.CharField(max_length=255, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Age Group: {self.age_group}"

class OrderTimingAnalytics(models.Model):
    """Track order timing patterns"""
    date = models.DateField()
    hour_of_day = models.IntegerField()  # 0-23
    day_of_week = models.IntegerField()  # 0-6 (Monday-Sunday)
    order_count = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    class Meta:
        unique_together = ('date', 'hour_of_day')

    def __str__(self):
        return f"Orders on {self.date} hour {self.hour_of_day}"

class DailyAnalyticsSnapshot(models.Model):
    """Daily snapshot of key metrics"""
    date = models.DateField(unique=True)
    new_customers = models.IntegerField(default=0)
    active_customers = models.IntegerField(default=0)
    total_orders = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    churn_rate = models.FloatField(default=0)  # % of customers inactive for 3+ months

    def __str__(self):
        return f"Analytics for {self.date}"