from rest_framework import serializers
from .models import *

# Tax Serializer
class TaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tax
        fields = ['tax_name', 'tax_percentage']

# Product Image Serializer
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_primary']

# Product Video Serializer
class ProductVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVideo
        fields = ['id', 'video']

# Attribute Serializer
class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ['id', 'name', 'value']

# Specification Serializer
class ProductSpecificationSerializer(serializers.ModelSerializer):
    attributes = AttributeSerializer(many=True)

    class Meta:
        model = ProductSpecification
        fields = ['id', 'attributes']

# Variant Serializer
class ProductVariantSerializer(serializers.ModelSerializer):
    attributes = AttributeSerializer(many=True)

    class Meta:
        model = ProductVariant
        fields = ['id', 'attributes', 'stock', 'price']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        models = Category
        fields = ["name", "description"]  
        
# Main Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    brand = serializers.StringRelatedField()
    tax_value = TaxSerializer()
    images = ProductImageSerializer(many=True, read_only=True)
    videos = ProductVideoSerializer(many=True, read_only=True)
    specifications = ProductSpecificationSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'product_code', 'name', 'brand', 'description', 'category', 
            'mrp', 'price', 'discount_price', 'stock', 'is_available',
            'price_before_tax', 'tax_amount', 'tax', 'tax_value',
            'youtube_url', 'broacher', 'images', 'videos', 
            'specifications', 'variants', 'created_at', 'updated_at'
        ]
