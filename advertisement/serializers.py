from rest_framework import serializers
from .models import ProductDropDownCategory, HeroCarousel, ProductSpecificationDescription, ProductListOnProduct

# Assuming you have ProductLightSerializer from inventory app
from inventory.serializers import ProductLightSerializer  # Import your existing serializer

class HeroCarouselSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeroCarousel
        fields = [
            'id', 'image', 'alt_text', 'head_one', 'head_two', 
            'description', 'button_text', 'button_link', 'order'
        ]

class ProductSpecificationDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSpecificationDescription
        fields = ['id', 'title', 'description', 'order']

class ProductListOnProductSerializer(serializers.ModelSerializer):
    product = ProductLightSerializer(read_only=True)
    
    class Meta:
        model = ProductListOnProduct
        fields = ['id', 'product', 'is_featured', 'order']

class ProductDropDownCategoryListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing categories"""
    class Meta:
        model = ProductDropDownCategory
        fields = ['id', 'name', 'slug', 'description', 'order']

class ProductDropDownCategoryDetailSerializer(serializers.ModelSerializer):
    """Complete serializer with all related data"""
    hero_carousels = HeroCarouselSerializer(many=True, read_only=True)
    specifications = ProductSpecificationDescriptionSerializer(many=True, read_only=True)
    category_products = ProductListOnProductSerializer(many=True, read_only=True)
    
    # Additional computed fields
    total_products = serializers.SerializerMethodField()
    featured_products = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductDropDownCategory
        fields = [
            'id', 'name', 'slug', 'description', 'order',
            'hero_carousels', 'specifications', 'category_products',
            'total_products', 'featured_products', 'date_added'
        ]
    
    def get_total_products(self, obj):
        return obj.category_products.count()
    
    def get_featured_products(self, obj):
        featured = obj.category_products.filter(is_featured=True)
        return ProductListOnProductSerializer(featured, many=True).data

# For creating/updating relationships
class ProductListOnProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductListOnProduct
        fields = ['dropdown_menu', 'product', 'is_featured', 'order']

class HeroCarouselCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeroCarousel
        fields = [
            'dropdown_menu', 'image', 'alt_text', 'head_one', 'head_two',
            'description', 'button_text', 'button_link', 'is_active', 'order'
        ]

class ProductSpecificationDescriptionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSpecificationDescription
        fields = ['dropdown_menu', 'title', 'description', 'is_active', 'order']