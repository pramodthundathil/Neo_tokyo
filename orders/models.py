from django.db import models
from django.conf import settings
from home.models import CustomUser
from inventory.models import Product

class Cart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=255, null=True, blank=True)
    shipping_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    coupon_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    referral_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_totals(self):
        item_total = sum(item.total_price for item in self.items.all())
        self.total_price = item_total + self.shipping_charges - self.coupon_discount - self.referral_discount
        self.save()

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

    @property
    def total_price(self):
        return self.quantity * self.price
