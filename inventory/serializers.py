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



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        models = Category
        fields = ["name", "description"]  


class ProductAttributeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttributeCategory
        fields = ['id', 'name']


class ProductAttributeSerializer(serializers.ModelSerializer):
    category = ProductAttributeCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductAttributeCategory.objects.all(), source='category', write_only=True
    )

    class Meta:
        model = ProductAttribute
        fields = ['id', 'category', 'category_id', 'name']


class ProductAttributeValueSerializer(serializers.ModelSerializer):
    attribute = ProductAttributeSerializer(read_only=True)
    attribute_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductAttribute.objects.all(), source='attribute', write_only=True
    )
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )

    class Meta:
        model = ProductAttributeValue
        fields = ['id', 'product_id', 'attribute', 'attribute_id']


class AttributeValueDetailSerializer(serializers.ModelSerializer):
    attribute_value = ProductAttributeValueSerializer(read_only=True)
    attribute_value_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductAttributeValue.objects.all(), source='attribute_value', write_only=True
    )

    class Meta:
        model = AttributeValueDetail
        fields = ['id', 'attribute_value', 'attribute_value_id', 'value']

        
# Main Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    brand = serializers.StringRelatedField()
    tax_value = TaxSerializer()
    images = ProductImageSerializer(many=True, read_only=True)
    videos = ProductVideoSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'product_code', 'name', 'brand', 'description', 'category', 
            'mrp', 'price', 'discount_price', 'stock', 'is_available',
            'price_before_tax', 'tax_amount', 'tax', 'tax_value',
            'youtube_url', 'broacher', 'images', 'videos', 
            'specifications', 'variants', 'created_at', 'updated_at'
        ]
