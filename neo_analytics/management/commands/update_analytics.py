from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count, Avg, F, Q, Window
from django.db.models.functions import ExtractHour, ExtractDay, TruncDate
from home.models import CustomUser
from orders.models import Order, OrderItem
from inventory.models import Product
from ...models import CustomerAnalytics, AgeGroupMetrics, DailyAnalyticsSnapshot, OrderTimingAnalytics

class Command(BaseCommand):
    help = 'Update all analytics data'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('Updating customer analytics...')
        self.update_customer_analytics()
        
        self.stdout.write('Updating age group metrics...')
        self.update_age_group_metrics()
        
        self.stdout.write('Updating daily analytics snapshot...')
        self.update_daily_snapshot()
        
        self.stdout.write('Updating order timing analytics...')
        self.update_order_timing()
        
        self.stdout.write(self.style.SUCCESS('Successfully updated all analytics!'))
    
    def update_customer_analytics(self):
        users = CustomUser.objects.all()
        count = 0
        for user in users:
            CustomerAnalytics.update_for_user(user)
            count += 1
            if count % 100 == 0:
                self.stdout.write(f'Processed {count} users...')
    
    def update_age_group_metrics(self):
        # Define age groups
        age_ranges = {
            '18-24': (18, 24),
            '25-34': (25, 34),
            '35-44': (35, 44),
            '45-54': (45, 54),
            '55+': (55, 200)
        }
        
        # Clear existing metrics
        AgeGroupMetrics.objects.all().delete()
        
        for age_range, (min_age, max_age) in age_ranges.items():
            users_in_range = CustomUser.objects.filter(age__gte=min_age, age__lte=max_age)
            if users_in_range.exists():
                # Calculate metrics for this age group
                orders = Order.objects.filter(user__in=users_in_range, order_status='PAID')
                total_revenue = orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
                avg_order = orders.aggregate(Avg('total_price'))['total_price__avg'] or 0
                
                # Most popular product for this age group
                popular_products = OrderItem.objects.filter(
                    order__in=orders
                ).values('product').annotate(
                    count=Count('id')
                ).order_by('-count')
                
                most_popular_id = None
                most_popular_name = ''
                if popular_products.exists():
                    most_popular_id = popular_products[0]['product']
                    try:
                        product = Product.objects.get(id=most_popular_id)
                        most_popular_name = product.name
                    except Product.DoesNotExist:
                        pass
                
                AgeGroupMetrics.objects.create(
                    age_group=age_range,
                    total_customers=users_in_range.count(),
                    average_order_value=avg_order,
                    total_revenue=total_revenue,
                    most_popular_product_id=most_popular_id,
                    most_popular_product_name=most_popular_name
                )
    
    def update_daily_snapshot(self):
        # Create snapshot for today
        today = timezone.now().date()
        
        # Get new customers today
        new_customers = CustomUser.objects.filter(date_joined__date=today).count()
        
        # Get active customers (ordered within last 90 days)
        ninety_days_ago = today - timedelta(days=90)
        active_customers = CustomUser.objects.filter(
            orders__created_at__date__gte=ninety_days_ago,
            orders__order_status='PAID'
        ).distinct().count()
        
        # Get today's orders
        today_orders = Order.objects.filter(created_at__date=today, order_status='PAID')
        total_orders = today_orders.count()
        total_revenue = today_orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        # Calculate churn rate
        six_months_ago = today - timedelta(days=180)
        three_months_ago = today - timedelta(days=90)
        
        # Customers who ordered 3-6 months ago
        customers_3_6_months = CustomUser.objects.filter(
            orders__created_at__date__gte=six_months_ago,
            orders__created_at__date__lt=three_months_ago,
            orders__order_status='PAID'
        ).distinct()
        
        # Of those, how many have not ordered in the last 3 months
        churned_customers = customers_3_6_months.exclude(
            orders__created_at__date__gte=three_months_ago,
            orders__order_status='PAID'
        ).count()
        
        churn_rate = (churned_customers / customers_3_6_months.count() * 100) if customers_3_6_months.count() > 0 else 0
        
        # Create or update snapshot
        snapshot, created = DailyAnalyticsSnapshot.objects.update_or_create(
            date=today,
            defaults={
                'new_customers': new_customers,
                'active_customers': active_customers,
                'total_orders': total_orders,
                'total_revenue': total_revenue,
                'average_order_value': avg_order_value,
                'churn_rate': churn_rate
            }
        )
        
        self.stdout.write(f'{"Created" if created else "Updated"} snapshot for {today}')
    
    def update_order_timing(self):
        # Clear existing timing analytics for today (to avoid duplicates)
        today = timezone.now().date()
        OrderTimingAnalytics.objects.filter(date=today).delete()
        
        # Get today's orders
        today_orders = Order.objects.filter(
            created_at__date=today,
            order_status='PAID'
        )
        
        # Group by hour
        hourly_data = today_orders.annotate(
            hour=ExtractHour('created_at'),
            day_of_week=ExtractDay('created_at') % 7  # Convert to 0-6 (Monday-Sunday)
        ).values('hour', 'day_of_week').annotate(
            order_count=Count('id'),
            total_revenue=Sum('total_price')
        )
        
        # Create timing analytics entries
        for data in hourly_data:
            OrderTimingAnalytics.objects.create(
                date=today,
                hour_of_day=data['hour'],
                day_of_week=data['day_of_week'],
                order_count=data['order_count'],
                total_revenue=data['total_revenue'] or 0
            )