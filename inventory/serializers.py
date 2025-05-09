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


# product pairing serializers 






class ProductLightSerializer(serializers.ModelSerializer):
    """Lightweight Product serializer for nested representations"""
    brand_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'product_code', 'name', 'brand_name', 'price', 'mrp', 'discount_price', 'is_available']
        
    def get_brand_name(self, obj):
        return str(obj.brand) if obj.brand else None

class ProductPairingSerializer(serializers.ModelSerializer):
    """Full serializer for ProductPairing objects"""
    paired_product_details = ProductLightSerializer(source='paired_product', read_only=True)
    
    class Meta:
        model = ProductPairing
        fields = [
            'id', 'primary_product', 'paired_product', 'paired_product_details',
            'pairing_strength', 'description', 'is_active'
        ]
        
class ProductPairingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating product pairings"""
    class Meta:
        model = ProductPairing
        fields = ['primary_product', 'paired_product', 'pairing_strength', 'description']
        
    def validate(self, data):
        # Ensure a product can't be paired with itself
        if data['primary_product'] == data['paired_product']:
            raise serializers.ValidationError("A product cannot be paired with itself.")
            
        # Check if this pairing already exists
        if ProductPairing.objects.filter(
            primary_product=data['primary_product'],
            paired_product=data['paired_product']
        ).exists():
            raise serializers.ValidationError("This product pairing already exists.")
            
        return data
    
    

class ProductWithPairingsSerializer(serializers.ModelSerializer):
    """Product serializer that includes paired products with their images"""
    paired_products = serializers.SerializerMethodField()
    brand_name = serializers.SerializerMethodField()
    primary_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'product_code', 'name', 'brand_name', 'description', 'category',
            'mrp', 'price', 'discount_price', 'stock', 'is_available',
            'youtube_url', 'whats_inside', 'primary_image', 'paired_products'
        ]
        
    def get_brand_name(self, obj):
        return str(obj.brand) if obj.brand else None
    
    def get_primary_image(self, obj):
        # Get the primary image for the product
        primary_image = obj.images.filter(is_primary=True).first()
        # If no primary image exists, get the first image
        if not primary_image:
            primary_image = obj.images.first()
        
        if primary_image:
            return self.context['request'].build_absolute_uri(primary_image.image.url)
        return None
        
    def get_paired_products(self, obj):
        pairings = obj.paired_products.filter(is_active=True)
        serializer = ProductPairingSerializer(
            pairings, 
            many=True,
            context={'request': self.context['request']}  # Pass the request context
        )
        return serializer.data
    


# recommendation system 

from .models import ProductRecommendation, ProductView


class ProductRecommendationSerializer(serializers.ModelSerializer):
    """Serializer for product recommendations"""
    recommended_product_details = ProductLightSerializer(source='recommended_product', read_only=True)
    recommendation_type_display = serializers.CharField(source='get_recommendation_type_display', read_only=True)
    
    class Meta:
        model = ProductRecommendation
        fields = [
            'id', 'source_product', 'recommended_product', 'recommended_product_details',
            'recommendation_type', 'recommendation_type_display', 'score'
        ]

class ProductViewSerializer(serializers.ModelSerializer):
    """Serializer for product views"""
    class Meta:
        model = ProductView
        fields = ['id', 'product', 'viewed_at']

class RecommendationResultSerializer(serializers.Serializer):
    """Serializer for recommendation results by type"""
    paired_with = ProductLightSerializer(many=True, required=False)
    similar = ProductLightSerializer(many=True, required=False)
    frequently_bought = ProductLightSerializer(many=True, required=False)
    popular_in_category = ProductLightSerializer(many=True, required=False) 
    trending = ProductLightSerializer(many=True, required=False)
    custom = ProductLightSerializer(many=True, required=False)
    recently_viewed = ProductLightSerializer(many=True, required=False)