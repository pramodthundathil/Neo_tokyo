from rest_framework import serializers
from .models import *

# Tax Serializer
class TaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tax
        fields = ['id','tax_name', 'tax_percentage']

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


class AttributeValueDetailSerializer(serializers.ModelSerializer):
   
    attribute_value_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductAttributeValue.objects.all(), source='attribute_value', write_only=True
    )

    class Meta:
        model = AttributeValueDetail
        fields = ['id', 'attribute_value_id', 'value']

class ProductAttributeValueSerializer(serializers.ModelSerializer):
    attribute = ProductAttributeSerializer(read_only=True)
    attribute_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductAttribute.objects.all(), source='attribute', write_only=True
    )
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )
    details = AttributeValueDetailSerializer(many=True, read_only=True)

    class Meta:
        model = ProductAttributeValue
        fields = ['id', 'product_id', 'attribute', 'attribute_id', 'details']


class AttributeValueDetailSerializer(serializers.ModelSerializer):
    attribute_value = ProductAttributeValueSerializer(read_only=True)
    attribute_value_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductAttributeValue.objects.all(), source='attribute_value', write_only=True
    )

    class Meta:
        model = AttributeValueDetail
        fields = ['id', 'attribute_value', 'attribute_value_id', 'value']



class VariantRelationshipAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VariantRelationshipAttribute
        fields = ['id', 'name']


class ProductVariantSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )
    variant_product = serializers.StringRelatedField(read_only=True)
    variant_product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='variant_product', write_only=True
    )
    relationship = VariantRelationshipAttributeSerializer(read_only=True)
    relationship_id = serializers.PrimaryKeyRelatedField(
        queryset=VariantRelationshipAttribute.objects.all(), source='relationship', write_only=True
    )

    class Meta:
        model = ProductVariant
        fields = [
            'id', 'product', 'product_id', 'variant_product', 'variant_product_id',
            'relationship', 'relationship_id', 'relationship_value'
        ]

        
# Main Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    brand = serializers.StringRelatedField()
    tax_value = TaxSerializer()
    images = ProductImageSerializer(many=True, read_only=True)
    videos = ProductVideoSerializer(many=True, read_only=True)
    attributes = ProductAttributeValueSerializer(many=True, read_only=True)
    variant_parent = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'product_code', 'name', 'brand', 'description', 'category', 
            'mrp', 'price', 'discount_price', 'stock', 'is_available',
            'price_before_tax', 'tax_amount', 'tax', 'tax_value',
            'youtube_url', 'broacher',"whats_inside","more_info", 'images', 'videos', 
            'attributes', 'variant_parent', 'created_at', 'updated_at'
        ]
