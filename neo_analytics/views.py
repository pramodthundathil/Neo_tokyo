from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Sum, Count, Avg, F, Q, Window
from django.db.models.functions import ExtractHour, ExtractDay, TruncDate
from django.utils import timezone
from datetime import timedelta
import datetime

from .models import CustomerAnalytics, AgeGroupMetrics, OrderTimingAnalytics, DailyAnalyticsSnapshot
from .serializers import (
    CustomerAnalyticsSerializer, 
    AgeGroupMetricsSerializer,
    OrderTimingAnalyticsSerializer, 
    DailyAnalyticsSnapshotSerializer,
    CustomerInsightsSerializer
)
from home.models import CustomUser
from orders.models import Order, OrderItem
from inventory.models import Product
from home.views import IsAdmin

class CustomerAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing customer analytics
    """
    queryset = CustomerAnalytics.objects.all()
    serializer_class = CustomerAnalyticsSerializer
    permission_classes = [IsAdmin, permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = CustomerAnalytics.objects.all()
        
        # Filter by active/inactive
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            is_active = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active)
            
        # Filter by minimum orders
        min_orders = self.request.query_params.get('min_orders')
        if min_orders:
            queryset = queryset.filter(total_orders__gte=int(min_orders))
            
        # Filter by minimum spent
        min_spent = self.request.query_params.get('min_spent')
        if min_spent:
            queryset = queryset.filter(total_spent__gte=float(min_spent))
        
        # Sort options
        sort_by = self.request.query_params.get('sort_by', 'total_spent')
        sort_direction = '-' if self.request.query_params.get('sort_direction', 'desc').lower() == 'desc' else ''
        queryset = queryset.order_by(f"{sort_direction}{sort_by}")
        
        return queryset

    @action(detail=False, methods=['post'])
    def refresh_analytics(self, request):
        """Recalculate analytics for all customers"""
        for user in CustomUser.objects.all():
            CustomerAnalytics.update_for_user(user)
        return Response({"status": "Analytics refreshed successfully"})

class CustomerInsightsView(APIView):
    """
    API endpoint for comprehensive customer insights
    """
    permission_classes = [IsAdmin, permissions.IsAuthenticated]
    
    def get(self, request):
        """Get comprehensive customer insights"""
        # Average Order Value
        paid_orders = Order.objects.filter(order_status='PAID')
        avg_order_value = paid_orders.aggregate(avg=Avg('total_price'))['avg'] or 0
        
        # Active/Inactive Customers
        three_months_ago = timezone.now() - timedelta(days=90)
        active_customers = CustomUser.objects.filter(
            orders__created_at__gte=three_months_ago,
            orders__order_status='PAID'
        ).distinct().count()
        
        total_customers = CustomUser.objects.count()
        inactive_customers = total_customers - active_customers
        
        # Most Loyal Customers (by number of orders)
        most_loyal = CustomUser.objects.annotate(
            order_count=Count('orders', filter=Q(orders__order_status='PAID'))
        ).filter(order_count__gt=0).order_by('-order_count')[:10]
        
        most_loyal_data = [
            {
                'id': user.id,
                'name': f"{user.first_name} {user.last_name}".strip(),
                'email': user.email,
                'order_count': user.order_count
            }
            for user in most_loyal
        ]
        
        # Top Customers by Revenue
        top_customers = CustomUser.objects.annotate(
            total_spent=Sum('orders__total_price', filter=Q(orders__order_status='PAID'))
        ).filter(total_spent__gt=0).order_by('-total_spent')[:10]
        
        top_customers_data = [
            {
                'id': user.id,
                'name': f"{user.first_name} {user.last_name}".strip(),
                'email': user.email,
                'total_spent': float(user.total_spent) if user.total_spent else 0
            }
            for user in top_customers
        ]
        
        # Least Spending Customers
        least_spending = CustomUser.objects.annotate(
            total_spent=Sum('orders__total_price', filter=Q(orders__order_status='PAID'))
        ).filter(total_spent__gt=0).order_by('total_spent')[:10]
        
        least_spending_data = [
            {
                'id': user.id,
                'name': f"{user.first_name} {user.last_name}".strip(),
                'email': user.email,
                'total_spent': float(user.total_spent) if user.total_spent else 0
            }
            for user in least_spending
        ]
        
        # Calculate average purchase frequency (days between orders)
        users_with_multiple_orders = CustomerAnalytics.objects.filter(total_orders__gt=1)
        avg_purchase_frequency = users_with_multiple_orders.aggregate(
            avg=Avg('purchase_frequency_days')
        )['avg'] or 0
        
        # Customer Churn Rate
        six_months_ago = timezone.now() - timedelta(days=180)
        active_six_months_ago = Order.objects.filter(
            created_at__gte=six_months_ago - timedelta(days=180),
            created_at__lte=six_months_ago,
            order_status='PAID'
        ).values('user').distinct().count()
        
        still_active = Order.objects.filter(
            user__in=Order.objects.filter(
                created_at__lte=six_months_ago,
                order_status='PAID'
            ).values('user'),
            created_at__gte=six_months_ago,
            order_status='PAID'
        ).values('user').distinct().count()
        
        churn_rate = 0
        if active_six_months_ago > 0:
            churn_rate = (active_six_months_ago - still_active) / active_six_months_ago * 100
        
        # Gender Analysis (assuming you store gender information)
        # This is a placeholder - adapt to your data model
        gender_analysis = {
            'unavailable': 'Gender analysis is not available in the current data model'
        }
        
        # Age Group Analysis
        age_ranges = {
            '18-24': (18, 24),
            '25-34': (25, 34),
            '35-44': (35, 44),
            '45-54': (45, 54),
            '55+': (55, 200)
        }
        
        age_group_data = []
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
                ).values('product__id', 'product__name').annotate(
                    count=Count('id')
                ).order_by('-count')
                
                most_popular = None
                if popular_products.exists():
                    most_popular = {
                        'id': popular_products[0]['product__id'],
                        'name': popular_products[0]['product__name'],
                        'count': popular_products[0]['count']
                    }
                
                age_group_data.append({
                    'age_group': age_range,
                    'customer_count': users_in_range.count(),
                    'total_revenue': float(total_revenue),
                    'average_order_value': float(avg_order),
                    'most_popular_product': most_popular
                })
        
        # Preferred Payment Methods
        # This is a placeholder - adapt to your payment data structure
        payment_methods = Order.objects.filter(
            order_status='PAID'
        ).values('payment_order_id').annotate(
            count=Count('id')
        ).order_by('-count')
        
        payment_methods_data = {
            method['payment_order_id'] if method['payment_order_id'] else 'Unknown': method['count']
            for method in payment_methods
        }
        
        # Return Rate (placeholder - adapt to your actual return/refund model)
        # This assumes you track returns separately
        return_rate = 0
        
        # Combine all insights
        insights = {
            'average_order_value': avg_order_value,
            'active_customers_count': active_customers,
            'inactive_customers_count': inactive_customers,
            'most_loyal_customers': most_loyal_data,
            'top_customers_by_revenue': top_customers_data,
            'least_spending_customers': least_spending_data,
            'average_purchase_frequency': avg_purchase_frequency,
            'customer_churn_rate': churn_rate,
            'gender_analysis': gender_analysis,
            'age_group_analysis': age_group_data,
            'preferred_payment_methods': payment_methods_data,
            'return_rate': return_rate
        }
        
        serializer = CustomerInsightsSerializer(insights)
        return Response(serializer.data)

class OrderTimingAnalyticsView(APIView):
    """
    API endpoint for order timing analysis
    """
    permission_classes = [IsAdmin, permissions.IsAuthenticated]
    
    def get(self, request):
        """Get order timing analysis"""
        # Initialize response data structure
        timing_data = {
            'hourly_distribution': [0] * 24,  # 24 hours
            'daily_distribution': [0] * 7,    # 7 days
            'hourly_revenue': [0] * 24,
            'daily_revenue': [0] * 7,
            'peak_hour': None,
            'peak_day': None
        }
        
        # Get parameters
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now().date() - timedelta(days=days)
        
        # Query orders within the time period
        orders = Order.objects.filter(
            created_at__date__gte=start_date,
            order_status='PAID'
        )
        
        # Hourly distribution
        hourly_data = orders.annotate(
            hour=ExtractHour('created_at')
        ).values('hour').annotate(
            count=Count('id'),
            revenue=Sum('total_price')
        ).order_by('hour')
        
        for data in hourly_data:
            hour = data['hour']
            timing_data['hourly_distribution'][hour] = data['count']
            timing_data['hourly_revenue'][hour] = float(data['revenue']) if data['revenue'] else 0
        
        # Daily distribution
        daily_data = orders.annotate(
            day=ExtractDay('created_at')
        ).values('day').annotate(
            count=Count('id'),
            revenue=Sum('total_price')
        ).order_by('day')
        
        for data in daily_data:
            day = data['day'] % 7  # Convert to 0-6 (Monday-Sunday)
            timing_data['daily_distribution'][day] = data['count']
            timing_data['daily_revenue'][day] = float(data['revenue']) if data['revenue'] else 0
        
        # Find peak hour and day
        if any(timing_data['hourly_distribution']):
            timing_data['peak_hour'] = timing_data['hourly_distribution'].index(max(timing_data['hourly_distribution']))
        
        if any(timing_data['daily_distribution']):
            timing_data['peak_day'] = timing_data['daily_distribution'].index(max(timing_data['daily_distribution']))
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            timing_data['peak_day_name'] = days[timing_data['peak_day']]
        
        return Response(timing_data)

class DashboardSummaryView(APIView):
    """
    API endpoint for dashboard summary
    """
    permission_classes = [IsAdmin, permissions.IsAuthenticated]
    
    def get(self, request):
        """Get dashboard summary data"""
        today = timezone.now().date()
        thirty_days_ago = today - timedelta(days=30)
        previous_thirty_days = thirty_days_ago - timedelta(days=30)
        
        # Current period metrics
        current_orders = Order.objects.filter(created_at__date__gte=thirty_days_ago, order_status='PAID')
        current_revenue = current_orders.aggregate(total=Sum('total_price'))['total'] or 0
        current_orders_count = current_orders.count()
        current_avg_order = current_revenue / current_orders_count if current_orders_count else 0
        
        # New customers in current period
        new_customers = CustomUser.objects.filter(date_joined__date__gte=thirty_days_ago).count()
        
        # Previous period metrics for comparison
        previous_orders = Order.objects.filter(
            created_at__date__gte=previous_thirty_days,
            created_at__date__lt=thirty_days_ago,
            order_status='PAID'
        )
        previous_revenue = previous_orders.aggregate(total=Sum('total_price'))['total'] or 0
        previous_orders_count = previous_orders.count()
        
        # Previous period new customers
        previous_new_customers = CustomUser.objects.filter(
            date_joined__date__gte=previous_thirty_days,
            date_joined__date__lt=thirty_days_ago
        ).count()
        
        # Calculate percentage changes
        revenue_change = ((current_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue else None
        orders_change = ((current_orders_count - previous_orders_count) / previous_orders_count * 100) if previous_orders_count else None
        customers_change = ((new_customers - previous_new_customers) / previous_new_customers * 100) if previous_new_customers else None
        
        # Daily revenue for chart
        daily_revenue = Order.objects.filter(
            created_at__date__gte=thirty_days_ago,
            order_status='PAID'
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            revenue=Sum('total_price')
        ).order_by('date')
        
        chart_data = [
            {
                'date': item['date'].strftime('%Y-%m-%d'),
                'revenue': float(item['revenue'])
            }
            for item in daily_revenue
        ]
        
        # Top selling products
        top_products = OrderItem.objects.filter(
            order__created_at__date__gte=thirty_days_ago,
            order__order_status='PAID'
        ).values('product__id', 'product__name').annotate(
            total_sold=Sum('quantity'),
            revenue=Sum(F('price') * F('quantity'))
        ).order_by('-total_sold')[:5]
        
        top_products_data = [
            {
                'id': item['product__id'],
                'name': item['product__name'],
                'total_sold': item['total_sold'],
                'revenue': float(item['revenue'])
            }
            for item in top_products
        ]
        
        summary = {
            'period_days': 30,
            'revenue': float(current_revenue),
            'revenue_change': float(revenue_change) if revenue_change is not None else None,
            'orders_count': current_orders_count,
            'orders_change': float(orders_change) if orders_change is not None else None,
            'average_order_value': float(current_avg_order),
            'new_customers': new_customers,
            'customers_change': float(customers_change) if customers_change is not None else None,
            'chart_data': chart_data,
            'top_products': top_products_data
        }
        
        return Response(summary)