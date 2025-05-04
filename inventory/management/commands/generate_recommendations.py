from django.core.management.base import BaseCommand
from django.db import transaction
import time
import logging

from ...models import Product
from ...recommendation_service import RecommendationService

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Generate product recommendations for all products'

    def add_arguments(self, parser):
        parser.add_argument(
            '--product_id',
            type=int,
            help='Generate recommendations for a specific product ID'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of products to process in each batch'
        )

    def handle(self, *args, **options):
        start_time = time.time()
        product_id = options.get('product_id')
        batch_size = options.get('batch_size')
        
        if product_id:
            try:
                product = Product.objects.get(id=product_id)
                self.stdout.write(f"Generating recommendations for product: {product.name}")
                
                with transaction.atomic():
                    RecommendationService.generate_similar_product_recommendations(product)
                    RecommendationService.generate_popular_in_category_recommendations(product)
                    RecommendationService.generate_frequently_bought_together(product)
                
                self.stdout.write(self.style.SUCCESS(
                    f"Successfully generated recommendations for product ID {product_id}"
                ))
            except Product.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Product with ID {product_id} not found"))
                return
        else:
            # Process all available products
            products = Product.objects.filter(is_available=True)
            total_products = products.count()
            
            self.stdout.write(f"Generating recommendations for {total_products} products")
            
            processed = 0
            for product in products:
                try:
                    with transaction.atomic():
                        RecommendationService.generate_similar_product_recommendations(product)
                        RecommendationService.generate_popular_in_category_recommendations(product)
                        RecommendationService.generate_frequently_bought_together(product)
                    
                    processed += 1
                    if processed % 10 == 0:
                        self.stdout.write(f"Processed {processed}/{total_products} products")
                        
                except Exception as e:
                    logger.error(f"Error generating recommendations for product {product.id}: {str(e)}")
            
            # Generate trending recommendations
            self.stdout.write("Generating trending recommendations")
            RecommendationService.generate_trending_recommendations()
                
            self.stdout.write(self.style.SUCCESS(
                f"Successfully generated recommendations for {processed} products"
            ))
        
        elapsed_time = time.time() - start_time
        self.stdout.write(f"Time taken: {elapsed_time:.2f} seconds")