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
    
   

@admin.register(ProductRecommendation)
class ProductRecommendationAdmin(admin.ModelAdmin):
    list_display = ('id', 'source_product_link', 'recommended_product_link', 
                    'recommendation_type', 'score', 'is_active')
    list_filter = ('recommendation_type', 'is_active', 'created_at')
    search_fields = ('source_product__name', 'recommended_product__name')
    list_editable = ('score', 'is_active')
    raw_id_fields = ('source_product', 'recommended_product')
    actions = ['refresh_recommendations']
    
    

@admin.register(ProductView)
class ProductViewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product_link', 'session_id', 'viewed_at')
    list_filter = ('viewed_at',)
    search_fields = ('product__name', 'user__username', 'session_id')
    raw_id_fields = ('user', 'product')
    date_hierarchy = 'viewed_at'
    
    