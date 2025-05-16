from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.core.cache import cache

from .models import Product
from .recommendation_service import RecommendationService

@receiver(post_save, sender=Product)
def update_product_recommendations(sender, instance, created, **kwargs):
    """
    When a product is created or updated, schedule recommendation updates
    """
    # Clear cache for this product
    cache_key = f'product_recommendations_{instance.id}'
    cache.delete(cache_key)
    
    # For new products, generate recommendations immediately
    if created:
        transaction.on_commit(
            lambda: RecommendationService.refresh_all_recommendations(product=instance)
        )
    # For updated products, only refresh if availability or key attributes changed
    elif hasattr(instance, '_changed_fields') and any(
        field in instance._changed_fields for field in 
        ['is_available', 'category_id', 'price', 'mrp', 'brand_id']
    ):
        transaction.on_commit(
            lambda: RecommendationService.refresh_all_recommendations(product=instance)
        )


from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ProductUpdate, ProductUpdateNotification
from orders.models import Order, OrderItem

# Signal to create notifications when a user purchases a product with existing updates
@receiver(post_save, sender=OrderItem)
def create_notifications_for_new_purchase(sender, instance, created, **kwargs):
    """
    When a user purchases a product, create notifications for any existing updates
    for that product.
    """
    if created and instance.order.payment_status == 'SUCCESS':
        # Get all updates for this product
        updates = ProductUpdate.objects.filter(product=instance.product)
        
        if updates.exists():
            # Create notifications for each update
            for update in updates:
                ProductUpdateNotification.objects.get_or_create(
                    user=instance.order.user,
                    product_update=update,
                    defaults={'is_read': False}
                )

# Signal to handle order status changes to SUCCESS
@receiver(post_save, sender=Order)
def handle_order_status_change(sender, instance, **kwargs):
    """
    When an order's payment status changes to SUCCESS, create notifications
    for all products in that order.
    """
    # Check if payment_status is SUCCESS
    if instance.payment_status == 'SUCCESS':
        # Get all order items in this order
        order_items = instance.items.all()
        
        # For each order item, get the product and create notifications
        for item in order_items:
            # Get all updates for this product
            updates = ProductUpdate.objects.filter(product=item.product)
            
            # Create notifications for each update
            for update in updates:
                ProductUpdateNotification.objects.get_or_create(
                    user=instance.user,
                    product_update=update,
                    defaults={'is_read': False}
                )

# Signal to clean up notifications when a product update is deleted
@receiver(post_delete, sender=ProductUpdate)
def clean_up_notifications(sender, instance, **kwargs):
    """
    When a product update is deleted, delete all associated notifications.
    """
    # Delete all notifications for this update
    ProductUpdateNotification.objects.filter(product_update=instance).delete()