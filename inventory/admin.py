from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages

from .models import ProductPairing, ProductRecommendation, ProductView

@admin.register(ProductPairing)
class ProductPairingAdmin(admin.ModelAdmin):
    list_display = ('id', 'primary_product_link', 'paired_product_link', 'pairing_strength', 'is_active')
    list_filter = ('is_active', 'pairing_strength', 'created_at')
    search_fields = ('primary_product__name', 'paired_product__name', 'description')
    list_editable = ('pairing_strength', 'is_active')
    raw_id_fields = ('primary_product', 'paired_product')
    
    def primary_product_link(self, obj):
        url = reverse('admin:your_app_name_product_change', args=[obj.primary_product.id])
        return format_html('<a href="{}">{}</a>', url, obj.primary_product.name)
    primary_product_link.short_description = 'Primary Product'
    
    def paired_product_link(self, obj):
        url = reverse('admin:your_app_name_product_change', args=[obj.paired_product.id])
        return format_html('<a href="{}">{}</a>', url, obj.paired_product.name)
    paired_product_link.short_description = 'Paired Product'

@admin.register(ProductRecommendation)
class ProductRecommendationAdmin(admin.ModelAdmin):
    list_display = ('id', 'source_product_link', 'recommended_product_link', 
                    'recommendation_type', 'score', 'is_active')
    list_filter = ('recommendation_type', 'is_active', 'created_at')
    search_fields = ('source_product__name', 'recommended_product__name')
    list_editable = ('score', 'is_active')
    raw_id_fields = ('source_product', 'recommended_product')
    actions = ['refresh_recommendations']
    
    def source_product_link(self, obj):
        url = reverse('admin:your_app_name_product_change', args=[obj.source_product.id])
        return format_html('<a href="{}">{}</a>', url, obj.source_product.name)
    source_product_link.short_description = 'Source Product'
    
    def recommended_product_link(self, obj):
        url = reverse('admin:your_app_name_product_change', args=[obj.recommended_product.id])
        return format_html('<a href="{}">{}</a>', url, obj.recommended_product.name)
    recommended_product_link.short_description = 'Recommended Product'
    
    def refresh_recommendations(self, request, queryset):
        from .recommendation_service import RecommendationService
        
        source_products = set()
        for recommendation in queryset:
            source_products.add(recommendation.source_product)
        
        for product in source_products:
            RecommendationService.refresh_all_recommendations(product)
        
        self.message_user(
            request, 
            f"Refreshed recommendations for {len(source_products)} products", 
            messages.SUCCESS
        )
    refresh_recommendations.short_description = "Refresh recommendations for selected products"

@admin.register(ProductView)
class ProductViewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product_link', 'session_id', 'viewed_at')
    list_filter = ('viewed_at',)
    search_fields = ('product__name', 'user__username', 'session_id')
    raw_id_fields = ('user', 'product')
    date_hierarchy = 'viewed_at'
    
    def product_link(self, obj):
        url = reverse('admin:your_app_name_product_change', args=[obj.product.id])
        return format_html('<a href="{}">{}</a>', url, obj.product.name)
    product_link.short_description = 'Product'