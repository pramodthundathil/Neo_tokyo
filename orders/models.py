from django.db import models
from django.conf import settings
from home.models import CustomUser, DeliveryAddress
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
    


# order handling models 

class Order(models.Model):

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    invoice_number = models.CharField(max_length=20, unique=True)

    delivery_address = models.ForeignKey(DeliveryAddress, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")

    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    price_before_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    total_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    bill_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    product_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    payment_status = models.CharField(
        max_length=20,
        choices=[('SUCCESS', 'Success'), ('FAILED', 'Failed'), ('PENDING', 'Pending')],
        default='PENDING'
    )
    order_status = models.CharField(
        max_length=20,
        choices=[('PENDING', 'Pending'), ('PAID', 'Paid'), ('FAILED', 'Failed')],
        default='PENDING'
    )
    payment_order_id = models.CharField(max_length=100, null=True, blank=True)
    def save(self, *args, **kwargs):
        # Fetch all related order items
        order_items = self.items.all()

        # Aggregate values from order items
        self.total_price = sum(item.price_after_tax for item in order_items)
        self.total_tax = sum(item.total_tax for item in order_items)
        self.price_before_tax = sum(item.total_price for item in order_items)
        self.product_discount = sum(item.product_discount for item in order_items)

        # Apply bill discount (if any)
        self.total_discount = self.product_discount + self.bill_discount
        self.total_price -= self.bill_discount  # Reduce the total price by the bill discount

        super(Order, self).save(*args, **kwargs)

    def __str__(self):

        return f"Order For {self.user} order number {self.invoice_number} amount {self.total_price}"



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_discount = models.DecimalField(max_digits=10, decimal_places=2)
    total_tax = models.DecimalField(max_digits=10, decimal_places=2)
    price_after_tax = models.DecimalField(max_digits=10, decimal_places=2)


    def save(self, *args, **kwargs):
        # Calculate total price for the quantity
        self.total_price = self.price * self.quantity

        # Calculate product discount per unit and multiply by quantity
        product_discount_per_unit = self.product.mrp - self.price
        self.product_discount = product_discount_per_unit * self.quantity

        # Calculate tax per product and multiply by quantity
        self.total_tax = self.product.tax_amount * self.quantity

        # Calculate price after tax
        self.price_after_tax = self.total_price + self.total_tax

        super(OrderItem, self).save(*args, **kwargs)

    def __str__(self):

        return f"Order  {self.order} :-  item {self.product} quantity {self.quantity} amount {self.total_price}"






