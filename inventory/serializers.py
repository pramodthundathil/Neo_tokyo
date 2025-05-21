from rest_framework import serializers
from .models import *
from interactions.serializers import ProductRatingSummarySerializer, ProductReviewSerializer, ReviewSerializer

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

class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'description']


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
    # Add variant product primary image
    variant_primary_image = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = [
            'id', 'product', 'product_id', 'variant_product', 'variant_product_id','variant_primary_image',
            'relationship', 'relationship_id', 'relationship_value'
        ]
    def get_variant_primary_image(self, obj):
        """Get the primary image for the variant product"""
        primary_image = ProductImage.objects.filter(
            product=obj.variant_product, 
            is_primary=True
        ).first()
        
        if primary_image:
            return ProductImageSerializer(primary_image).data
        
        # If no primary image exists, try to get the first image
        first_image = ProductImage.objects.filter(
            product=obj.variant_product
        ).first()
        
        if first_image:
            return ProductImageSerializer(first_image).data
            
        return None
        
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
    category = serializers.StringRelatedField(read_only=True)
    subcategory = serializers.StringRelatedField(read_only=True)
    brand = serializers.StringRelatedField(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    videos = ProductVideoSerializer(many=True, read_only=True)
    attributes = ProductAttributeValueSerializer(many=True, read_only=True)
    variant_parent = ProductVariantSerializer(many=True, read_only=True)

    # Add reviews to ProductSerializer
    approved_reviews = serializers.SerializerMethodField()
    rating_summary = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'product_code', 'name', 'brand', 'description','warranty_info', 'category','subcategory', 
            'mrp', 'price', 'discount_price', 'stock', 'is_available',
            'price_before_tax', 'tax_amount', 'tax', 'tax_value',
            'youtube_url', 'broacher', "whats_inside", "more_info", 'images', 
            'videos', 'attributes', 'variant_parent', 'approved_reviews', 
            'rating_summary', 'created_at', 'updated_at'
        ]

    def get_approved_reviews(self, obj):
        """Get only approved reviews for this product"""
        approved_reviews = obj.reviews.all()
        return ReviewSerializer(approved_reviews, many=True).data
    
    def get_rating_summary(self, obj):
        """Get rating summary for this product"""
        try:
            return ProductRatingSummarySerializer(obj.rating_summary).data
        except:
            return None


# product pairing serializers 


class ProductLightSerializer(serializers.ModelSerializer):
    """Lightweight Product serializer for nested representations"""
    brand_name = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'product_code', 'name', 'brand_name', 'price', 'mrp', 'discount_price', "images", 'is_available']
        
    def get_brand_name(self, obj):
        return str(obj.brand) if obj.brand else None

class ProductPairingSerializer(serializers.ModelSerializer):
    """Serializer for product pairings that includes paired product details with image"""
    paired_product_details = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductPairing
        fields = ['id', 'paired_product_details', 'pairing_strength', 'description']
    
    def get_paired_product_details(self, obj):
        paired_product = obj.paired_product
        
        # Get the primary image for the paired product
        primary_image = None
        primary_image_obj = paired_product.images.filter(is_primary=True).first()
        
        # If no primary image exists, get the first image
        if not primary_image_obj:
            primary_image_obj = paired_product.images.first()
        
        if primary_image_obj:
            primary_image = self.context['request'].build_absolute_uri(primary_image_obj.image.url)
        
        # Return product details with primary image
        return {
            'id': paired_product.id,
            'product_code': paired_product.product_code,
            'name': paired_product.name,
            'brand_name': str(paired_product.brand) if paired_product.brand else None,
            'price': paired_product.price,
            'discount_price': paired_product.discount_price,
            'is_available': paired_product.is_available,
            'primary_image': primary_image
        }


        
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
    
    class Meta:
        model = Product
        fields = [
            'id', 'product_code', 'name', 'brand_name', 'description', 'category',
            'mrp', 'price', 'discount_price', 'stock', 'is_available',
            'youtube_url', 'whats_inside', 'paired_products'
        ]
        
    def get_brand_name(self, obj):
        return str(obj.brand) if obj.brand else None
        
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



# product featured product ...............................................


class ProductMinimalSerializer(serializers.ModelSerializer):
    """Minimal serializer for base Product model"""
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', "mrp"]


class FeaturedProductSerializer(serializers.ModelSerializer):
    """Serializer for customer-facing FeaturedProducts data"""
    product_details = ProductMinimalSerializer(source='product', read_only=True)
    
    class Meta:
        model = FeaturedProducts
        fields = [
            'id', 'featured_name', 'tagline', 'cpu', 'cpu_clock', 
            'gpu', 'gpu_vram', 'ram', 'storage', 'banner_image',
            'is_available', 'product_details'
        ]


class FeaturedProductAdminSerializer(serializers.ModelSerializer):
    """Serializer for admin operations with full details"""
    product_details = ProductMinimalSerializer(source='product', read_only=True)
    
    class Meta:
        model = FeaturedProducts
        fields = '__all__'
        
    def validate(self, data):
        """Additional validation for admin operations"""
        # Example: Ensure product exists if product_id is provided
        if 'product' in data and data['product'] is None:
            raise serializers.ValidationError("A valid product must be selected")
        return data



#product driver update serializers


class ProductLightMyProductSerializer(serializers.ModelSerializer):
    """Lightweight Product serializer for nested representations"""
    brand_name = serializers.SerializerMethodField()
    primary_image = serializers.SerializerMethodField()
    attributes = ProductAttributeValueSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'product_code', 'name', 'brand_name', 'attributes', 'price', 'mrp', 'discount_price', 'primary_image', 'is_available']
        
    def get_brand_name(self, obj):
        return str(obj.brand) if obj.brand else None
    
    def get_primary_image(self, obj):
        """Get only the primary image for the product"""
        request = self.context.get('request')
        primary_image = obj.images.filter(is_primary=True).first()
        
        if not primary_image:
            # Fallback to first image if there's no primary image
            primary_image = obj.images.first()
            
        if request and primary_image and primary_image.image:
            return {
                'id': primary_image.id,
                'image': primary_image.image.url,
                'image_url': request.build_absolute_uri(primary_image.image.url),
                'is_primary': primary_image.is_primary
            }
        return None
    

from .models import ProductUpdate, ProductUpdateNotification

class ProductUpdateSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_brand = serializers.CharField(source='product.brand', read_only=True)
    days_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductUpdate
        fields = [
            'id', 'product', 'product_name', 'product_brand', 
            'name', 'version', 'description', 'update_file', 
            'download_url', 'release_date', 'is_critical', 'days_ago'
        ]
    
    def get_days_ago(self, obj):
        """Return days since this update was released"""
        from django.utils import timezone
        import datetime
        
        now = timezone.now()
        delta = now - obj.release_date
        
        if delta.days < 1:
            hours = delta.seconds // 3600
            if hours < 1:
                return "Just now"
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif delta.days == 1:
            return "Yesterday"
        elif delta.days < 7:
            return f"{delta.days} days ago"
        elif delta.days < 30:
            weeks = delta.days // 7
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        else:
            months = delta.days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"


class ProductUpdateNotificationSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_update.product.name', read_only=True)
    update_name = serializers.CharField(source='product_update.name', read_only=True)
    update_version = serializers.CharField(source='product_update.version', read_only=True)
    update_description = serializers.CharField(source='product_update.description', read_only=True)
    download_url = serializers.URLField(source='product_update.download_url', read_only=True)
    is_critical = serializers.BooleanField(source='product_update.is_critical', read_only=True)
    
    class Meta:
        model = ProductUpdateNotification
        fields = [
            'id', 'user', 'product_update', 'product_name', 'update_name',
            'update_version', 'update_description', 'download_url',
            'is_critical', 'created_at', 'is_read'
        ]
        read_only_fields = ['user', 'product_update', 'created_at']