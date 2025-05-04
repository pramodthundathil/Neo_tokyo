from rest_framework import serializers
from .models import *

# Tax Serializer
class TaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tax
        fields = ['id','tax_name', 'tax_percentage']


class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'image_url', 'is_primary']
        read_only_fields = ['image_url']
    
    def get_image_url(self, obj):
        """Return the complete URL for the image"""
        request = self.context.get('request')
        if request and obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None

class ProductVideoSerializer(serializers.ModelSerializer):
    video_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductVideo
        fields = ['id', 'video', 'video_url']
        read_only_fields = ['video_url']
    
    def get_video_url(self, obj):
        """Return the complete URL for the video"""
        request = self.context.get('request')
        if request and obj.video:
            return request.build_absolute_uri(obj.video.url)
        return None

# For use in bulk uploading multiple media files
class BulkProductMediaUploadSerializer(serializers.Serializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        required=False
    )
    videos = serializers.ListField(
        child=serializers.FileField(),
        required=False
    )
    primary_image_index = serializers.IntegerField(required=False, default=0)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id","name", "description"]  


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id","name"]


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

class ProductAttributeCategorySerializerForSort(serializers.ModelSerializer):
    attributes = ProductAttributeSerializer(many=True, read_only=True)

    class Meta:
        model = ProductAttributeCategory
        fields = ['id', 'name', 'attributes']


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


# class AttributeValueDetailSerializer(serializers.ModelSerializer):
#     attribute_value = ProductAttributeValueSerializer(read_only=True)
#     attribute_value_id = serializers.PrimaryKeyRelatedField(
#         queryset=ProductAttributeValue.objects.all(), source='attribute_value', write_only=True
#     )

#     class Meta:
#         model = AttributeValueDetail
#         fields = ['id', 'attribute_value', 'attribute_value_id', 'value']



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
# class ProductSerializer(serializers.ModelSerializer):
#     category = serializers.StringRelatedField()
#     brand = serializers.StringRelatedField()
#     # tax_value = TaxSerializer()
#     images = ProductImageSerializer(many=True, read_only=True)
#     videos = ProductVideoSerializer(many=True, read_only=True)
#     attributes = ProductAttributeValueSerializer(many=True, read_only=True)
#     variant_parent = ProductVariantSerializer(many=True, read_only=True)

#     class Meta:
#         model = Product
#         fields = [
#             'id', 'product_code', 'name', 'brand', 'description', 'category', 
#             'mrp', 'price', 'discount_price', 'stock', 'is_available',
#             'price_before_tax', 'tax_amount', 'tax', 'tax_value',
#             'youtube_url', 'broacher',"whats_inside","more_info", 'images', 'videos', 
#             'attributes', 'variant_parent', 'created_at', 'updated_at'
#         ]


from rest_framework import serializers
from .models import Product, Brand, Category

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    brand = serializers.PrimaryKeyRelatedField(queryset=Brand.objects.all())
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
            'youtube_url', 'broacher', "whats_inside", "more_info", 'images', 
            'videos', 'attributes', 'variant_parent', 'created_at', 'updated_at'
        ]
