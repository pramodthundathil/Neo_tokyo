from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem
from inventory.models import Product, ProductImage
from inventory.serializers import ProductImageSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_stock = serializers.CharField(source="product.stock", read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name',"product_stock", 'quantity', 'price', 'total_price', 'primary_image']
    
    def get_primary_image(self, obj):
        try:
            primary_image = ProductImage.objects.filter(product=obj.product, is_primary=True).first()
            if primary_image:
                return {
                    'id': primary_image.id,
                    'image': primary_image.image.url if primary_image.image else None
                }
            # Fallback to first image if no primary image
            first_image = obj.product.images.first()
            if first_image:
                return {
                    'id': first_image.id,
                    'image': first_image.image.url if first_image.image else None
                }
        except Exception:
            pass
        return None


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'session_key', 'items', 'total_price',"coupon_discount","referral_discount"]

    def get_total_price(self, obj):
        return sum(item.total_price for item in obj.items.all())
    



class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    product_image = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'product_image', 'quantity', 'price', 
            'total_price', 'product_discount', 'total_tax', 'price_after_tax'
        ]
        read_only_fields = fields
    
    def get_product_name(self, obj):
        return obj.product.name if obj.product else None
        
    def get_product_image(self, obj):
        if obj.product:
            primary_image = obj.product.images.filter(is_primary=True).first()
            if primary_image:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(primary_image.image.url)
                return primary_image.image.url
        return None

class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_name = serializers.SerializerMethodField()
    delivery_address_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'user', 'user_name', 'invoice_number', 'delivery_address',
            'delivery_address_details', 'total_price', 'total_tax', 
            'price_before_tax', 'total_discount', 'bill_discount', 
            'product_discount', 'payment_status','payment_method', 'order_status','delivery_status', 
            'payment_order_id', 'created_at', 'updated_at', 'items'
        ]
        read_only_fields = fields
    
    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}" if obj.user else None
    
    def get_delivery_address_details(self, obj):
        if not obj.delivery_address:
            return None
        
        address = obj.delivery_address
        return {
            "delivery_person_name":address.delivery_person_name,
            'phone_number': address.phone_number,
            'district': address.district,
            'state': address.state,
            'postal_code': address.zip_code,
            'address':address.address,
            'country': address.country
        }

class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status', 'order_status','delivery_status', 'bill_discount', 'delivery_address']
    
    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        
        # Recalculate totals if bill discount is updated
        if 'bill_discount' in validated_data:
            instance.calculate_totals()
        
        return instance