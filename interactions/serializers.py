from rest_framework import serializers
from .models import Review, ReviewImage, ProductRatingSummary
from inventory.models import Product
from home.models import CustomUser

class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = ['id', 'image']
        read_only_fields = ['id']


class ReviewSerializer(serializers.ModelSerializer):
    images = ReviewImageSerializer(many=True, required=False, read_only=True)
    user = serializers.ReadOnlyField(source='user.first_name')
    profile_image = serializers.ImageField(source="user.profile_picture", read_only=True)
    profile_image_url = serializers.URLField(source ='user.profile_picture_url', read_only=True )
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False,
        max_length=5  # Maximum 5 images per review
    )
    
    class Meta:
        model = Review
        fields = [
            'id', 'product', 'user',"profile_image","profile_image_url", 'rating', 'title', 'comment',
            'created_at', 'updated_at', 'is_verified_purchase', 
            'is_approved', 'images', 'uploaded_images'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user','profile_image','profile_image_url', 'is_verified_purchase', 'is_approved']
    
    def validate_product(self, value):
        if not value.is_available:
            raise serializers.ValidationError("Cannot review unavailable products")
        return value
    
    def validate(self, data):
        # Check for existing review by this user for this product
        request = self.context.get('request')
        if request and request.method == 'POST':
            product = data.get('product')
            user = request.user
            if Review.objects.filter(product=product, user=user).exists():
                raise serializers.ValidationError("You have already reviewed this product")
        return data
    
    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        review = Review.objects.create(**validated_data)
        
        # Check if user has purchased this product
        # This is just a placeholder - implement your actual verification logic
        user = validated_data.get('user')
        product = validated_data.get('product')
        # if Order.objects.filter(user=user, items__product=product, status='completed').exists():
        #     review.is_verified_purchase = True
        #     review.save()
        
        # Process uploaded images
        for image in uploaded_images:
            ReviewImage.objects.create(review=review, image=image)
        
        return review


class ProductRatingSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRatingSummary
        fields = [
            'average_rating', 'total_reviews',
            'five_star_count', 'four_star_count', 'three_star_count',
            'two_star_count', 'one_star_count'
        ]


class ProductReviewSerializer(serializers.ModelSerializer):
    """Serializer for displaying reviews on product detail page"""
    reviews = ReviewSerializer(many=True, read_only=True, source='get_approved_reviews')
    rating_summary = ProductRatingSummarySerializer(source='get_rating_summary', read_only=True)
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'rating_summary', 'reviews']
        read_only_fields = ['id', 'name', 'rating_summary', 'reviews']



from .models import GrievanceTicket

class GrievanceTicketSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    class Meta:
        model = GrievanceTicket
        fields = ['id', 'date_created', 'date_updated', 'product','product_name',"image","link", 'product_serial_number', 
                 'grievance', 'conclusion', 'ticket_id',"is_concluded"]
        read_only_fields = ['id', 'date_created', 'date_updated', 'ticket_id', 'user',"conclusion"]

    def create(self, validated_data):
        # Automatically set the user to the currently authenticated user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class GrievanceTicketAdminSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    class Meta:
        model = GrievanceTicket
        fields = ['id', 'date_created', 'date_updated', 'user', 'product', 'product_name',"image","link", 'product_serial_number',
                 'grievance', 'conclusion', 'ticket_id',"is_concluded"]
        read_only_fields = ['id', 'date_created', 'date_updated', 'ticket_id', 'user',
                           'product', 'product_serial_number', 'grievance']