from rest_framework import serializers
from .models import Cart, CartItem
from inventory.models import Product

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)  # Remove `source`

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price', 'total_price']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'session_key', 'items', 'total_price',"coupon_discount","referral_discount"]

    def get_total_price(self, obj):
        return sum(item.total_price for item in obj.items.all())
    

