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