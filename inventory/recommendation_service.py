from django.db.models import Count, Avg, Q, F
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import logging

from .models import Product, ProductView, ProductRecommendation, ProductPairing, Category

logger = logging.getLogger(__name__)

from django.core.cache import cache

class RecommendationService:
    """Service for generating and retrieving product recommendations"""
    
    @staticmethod
    def get_recommendations(product, recommendation_type='similar', limit=5):
        """Get recommendations for a product of a specific type"""
        # Check cache first
        cache_key = f'product_rec_{product.id}_{recommendation_type}_{limit}'
        cached_results = cache.get(cache_key)
        
        if cached_results is not None:
            return cached_results
        
        # If not in cache, fetch from database
        recommendations = ProductRecommendation.objects.filter(
            source_product=product,
            recommendation_type=recommendation_type,
            is_active=True,
            recommended_product__is_available=True
        ).select_related('recommended_product')[:limit]
        
        results = [rec.recommended_product for rec in recommendations]
        
        # Cache results for 1 hour (3600 seconds)
        cache.set(cache_key, results, 3600)
        
        return results
    
    @staticmethod
    def get_all_recommendations(product, limit_per_type=5):
        """Get all types of recommendations for a product"""
        # Check cache first
        cache_key = f'product_all_rec_{product.id}_{limit_per_type}'
        cached_results = cache.get(cache_key)
        
        if cached_results is not None:
            return cached_results
        
        result = {}
        
        # Get predefined pairings first (highest priority)
        paired_products = ProductPairing.objects.filter(
            primary_product=product,
            is_active=True
        ).order_by('-pairing_strength')[:limit_per_type]
        result['paired_with'] = [pair.paired_product for pair in paired_products]
        
        # Get other recommendation types
        for rec_type, _ in ProductRecommendation.RECOMMENDATION_TYPES:
            recs = RecommendationService.get_recommendations(
                product, 
                recommendation_type=rec_type,
                limit=limit_per_type
            )
            if recs:
                result[rec_type] = recs
        
        # Cache results for 1 hour (3600 seconds)
        cache.set(cache_key, result, 3600)
                
        return result
    
    # Other methods remain the same...
    
    @staticmethod
    def refresh_all_recommendations(product=None):
        """Refresh all recommendations for a product or all products"""
        products = [product] if product else Product.objects.filter(is_available=True)
        
        for product in products:
            try:
                # Clear cache for this product
                cache.delete(f'product_all_rec_{product.id}_5')  # Default limit
                cache.delete(f'product_all_rec_{product.id}_10')  # Common limit
                
                for rec_type, _ in ProductRecommendation.RECOMMENDATION_TYPES:
                    cache.delete(f'product_rec_{product.id}_{rec_type}_5')
                    cache.delete(f'product_rec_{product.id}_{rec_type}_10')
                
                # Generate new recommendations
                RecommendationService.generate_similar_product_recommendations(product)
                RecommendationService.generate_popular_in_category_recommendations(product)
                RecommendationService.generate_frequently_bought_together(product)
            except Exception as e:
                logger.error(f"Error generating recommendations for product {product.id}: {str(e)}")
                
        # Generate global trending recommendations
        try:
            # Clear trending cache
            cache.delete('trending_products_10')
            cache.delete('trending_products_20')
            
            RecommendationService.generate_trending_recommendations()
        except Exception as e:
            logger.error(f"Error generating trending recommendations: {str(e)}")
    """Service for generating and retrieving product recommendations"""
    
    @staticmethod
    def get_recommendations(product, recommendation_type='similar', limit=5):
        """Get recommendations for a product of a specific type"""
        recommendations = ProductRecommendation.objects.filter(
            source_product=product,
            recommendation_type=recommendation_type,
            is_active=True,
            recommended_product__is_available=True
        ).select_related('recommended_product')[:limit]
        
        return [rec.recommended_product for rec in recommendations]
    
    @staticmethod
    def get_all_recommendations(product, limit_per_type=5):
        """Get all types of recommendations for a product"""
        result = {}
        
        # Get predefined pairings first (highest priority)
        paired_products = ProductPairing.objects.filter(
            primary_product=product,
            is_active=True
        ).order_by('-pairing_strength')[:limit_per_type]
        result['paired_with'] = [pair.paired_product for pair in paired_products]
        
        # Get other recommendation types
        for rec_type, _ in ProductRecommendation.RECOMMENDATION_TYPES:
            recs = RecommendationService.get_recommendations(
                product, 
                recommendation_type=rec_type,
                limit=limit_per_type
            )
            if recs:
                result[rec_type] = recs
                
        return result
    
    @staticmethod
    def generate_similar_product_recommendations(product, limit=10):
        """Generate similar product recommendations based on product attributes"""
        
        # Clear existing recommendations of this type
        ProductRecommendation.objects.filter(
            source_product=product,
            recommendation_type='similar'
        ).delete()
        
        category = product.category
        brand = product.brand
        price_range_min = product.price * Decimal('0.7')  # 70% of product price
        price_range_max = product.price * Decimal('1.3')  # 130% of product price
        
        # Find similar products with scoring based on attributes
        similar_products = Product.objects.filter(
            is_available=True
        ).exclude(
            id=product.id
        )
        
        recommendations = []
        
        # Process each potential similar product
        for similar in similar_products:
            score = Decimal('0')
            
            # Same category gets a high score
            if similar.category == category:
                score += Decimal('3')
                
            # Same brand gets a medium score
            if brand and similar.brand == brand:
                score += Decimal('2')
                
            # Similar price range gets a low score
            if price_range_min <= similar.price <= price_range_max:
                score += Decimal('1')
                
            # Must have at least one matching attribute
            if score > 0:
                recommendations.append(
                    ProductRecommendation(
                        source_product=product,
                        recommended_product=similar,
                        recommendation_type='similar',
                        score=score
                    )
                )
        
        # Sort by score and limit
        recommendations.sort(key=lambda x: x.score, reverse=True)
        recommendations = recommendations[:limit]
        
        # Save all recommendations
        if recommendations:
            ProductRecommendation.objects.bulk_create(recommendations)
            
        return recommendations
    
    @staticmethod
    def generate_popular_in_category_recommendations(product, days=30, limit=10):
        """Generate recommendations based on popular products in the same category"""
        
        # Clear existing recommendations of this type
        ProductRecommendation.objects.filter(
            source_product=product,
            recommendation_type='popular_in_category'
        ).delete()
        
        category = product.category
        
        # Time frame for popularity calculation
        start_date = timezone.now() - timedelta(days=days)
        
        # Find popular products in the same category based on view count
        popular_products = Product.objects.filter(
            category=category,
            is_available=True,
            productview__viewed_at__gte=start_date
        ).exclude(
            id=product.id
        ).annotate(
            view_count=Count('productview')
        ).order_by('-view_count')[:limit]
        
        # Create recommendations
        recommendations = []
        max_views = 1  # Prevent division by zero
        
        # Get the max view count for normalization
        if popular_products:
            max_views = max(p.view_count for p in popular_products) or 1
            
        for popular in popular_products:
            # Normalize score between 1-5 based on view count
            score = Decimal(popular.view_count) / Decimal(max_views) * Decimal('5')
            score = min(Decimal('5'), max(Decimal('1'), score))  # Clamp between 1-5
            
            recommendations.append(
                ProductRecommendation(
                    source_product=product,
                    recommended_product=popular,
                    recommendation_type='popular_in_category',
                    score=score
                )
            )
        
        # Save all recommendations
        if recommendations:
            ProductRecommendation.objects.bulk_create(recommendations)
            
        return recommendations
    
    @staticmethod
    def generate_trending_recommendations(days=7, limit=20):
        """Generate trending product recommendations based on recent views"""
        
        # Clear existing trending recommendations
        ProductRecommendation.objects.filter(
            recommendation_type='trending'
        ).delete()
        
        # Time frame for trending calculation
        start_date = timezone.now() - timedelta(days=days)
        
        # Find trending products based on recent view count
        trending_products = Product.objects.filter(
            is_available=True,
            productview__viewed_at__gte=start_date
        ).annotate(
            view_count=Count('productview')
        ).order_by('-view_count')[:50]  # Get top 50 to process
        
        # Group by category to ensure diversity
        trending_by_category = {}
        for product in trending_products:
            category_id = product.category_id
            if category_id not in trending_by_category:
                trending_by_category[category_id] = []
            trending_by_category[category_id].append(product)
        
        # Get top products from each category
        diverse_trending = []
        for category_products in trending_by_category.values():
            diverse_trending.extend(category_products[:3])  # Top 3 from each category
            
        # Limit to requested amount
        diverse_trending = diverse_trending[:limit]
        
        # For each trending product, create recommendations to itself
        recommendations = []
        max_views = max(p.view_count for p in diverse_trending) if diverse_trending else 1
        
        for trending in diverse_trending:
            # Normalize score between 1-5 based on view count
            score = Decimal(trending.view_count) / Decimal(max_views) * Decimal('5')
            score = min(Decimal('5'), max(Decimal('1'), score))  # Clamp between 1-5
            
            # Create a self-recommendation for trending products
            recommendations.append(
                ProductRecommendation(
                    source_product=trending,
                    recommended_product=trending,
                    recommendation_type='trending',
                    score=score
                )
            )
        
        # Save all recommendations
        if recommendations:
            ProductRecommendation.objects.bulk_create(recommendations)
            
        return recommendations
    
    @staticmethod
    def generate_frequently_bought_together(product, limit=10):
        """
        Generate 'frequently bought together' recommendations
        This is a placeholder implementation - in a real system, this would use
        actual order data to determine which products are frequently purchased together
        """
        # In a real implementation, this would analyze order data
        # For now, we'll use a simplified approach based on category + price similarity
        
        # Clear existing recommendations of this type
        ProductRecommendation.objects.filter(
            source_product=product,
            recommendation_type='frequently_bought'
        ).delete()
        
        category = product.category
        complementary_categories = Category.objects.filter(
            # This filter would ideally use a predefined relationship
            # between complementary categories
            # For now, just get similar categories
            id__ne=category.id
        )[:3]
        
        # Find complementary products
        complementary_products = Product.objects.filter(
            is_available=True,
            category__in=complementary_categories
        ).exclude(
            id=product.id
        )[:20]  # Limit to 20 for processing
        
        # Create recommendations
        recommendations = []
        
        for complementary in complementary_products:
            # Simple scoring based on price compatibility
            # Products with similar price points tend to be bought together
            price_ratio = min(product.price, complementary.price) / max(product.price, complementary.price)
            score = Decimal(price_ratio) * Decimal('5')
            
            recommendations.append(
                ProductRecommendation(
                    source_product=product,
                    recommended_product=complementary,
                    recommendation_type='frequently_bought',
                    score=score
                )
            )
        
        # Sort by score and limit
        recommendations.sort(key=lambda x: x.score, reverse=True)
        recommendations = recommendations[:limit]
        
        # Save all recommendations
        if recommendations:
            ProductRecommendation.objects.bulk_create(recommendations)
            
        return recommendations
    
    @staticmethod
    def refresh_all_recommendations(product=None):
        """Refresh all recommendations for a product or all products"""
        products = [product] if product else Product.objects.filter(is_available=True)
        
        for product in products:
            try:
                RecommendationService.generate_similar_product_recommendations(product)
                RecommendationService.generate_popular_in_category_recommendations(product)
                RecommendationService.generate_frequently_bought_together(product)
            except Exception as e:
                logger.error(f"Error generating recommendations for product {product.id}: {str(e)}")
                
        # Generate global trending recommendations
        try:
            RecommendationService.generate_trending_recommendations()
        except Exception as e:
            logger.error(f"Error generating trending recommendations: {str(e)}")