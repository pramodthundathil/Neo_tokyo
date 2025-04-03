from rest_framework import serializers
from .models import Cart, CartItem
from inventory.models import Product, ProductImage
from inventory.serializers import ProductImageSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price', 'total_price', 'primary_image']
    
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
    

