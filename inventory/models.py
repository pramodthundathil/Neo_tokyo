from django.db import models
from decimal import Decimal
import random

### inventory product model details start #############################################
# Subcategories and Variants: Introduce additional models like ProductVariant and Attribute to 
# capture specific details such as type (DDR4), size (4GB, 8GB), and brand.Relationships: Use ManyToManyField for flexible attribute association
# USAGE
# Create categories such as PC Components with subcategories like RAM.
# Add attributes for types, sizes, etc.
# Create variants for specific products with different configurations.
#tax model

class Tax(models.Model):
    tax_name = models.CharField(max_length=20)
    tax_percentage = models.FloatField()

    def __str__(self):
        return '{}  {} %'.format(str(self.tax_name),(self.tax_percentage))

# Category Model
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True, help_text="Category Will Be Unique")
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL, blank=True, null=True, related_name='subcategories'
    )

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    product_code = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=255)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    mrp = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    stock = models.PositiveIntegerField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # youtube and broachers 
    youtube_url = models.URLField(null=True, blank=True)
    broacher = models.FileField(upload_to="product_broacher")
    whats_inside = models.TextField()
    more_info = models.URLField(null=True, blank=True)

    # Tax Calculations
    price_before_tax = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=Decimal('0.00'))
    TAX_CHOICES = (
        ("Inclusive", "Inclusive"),
        ("Exclusive", "Exclusive"),
    )
    tax = models.CharField(max_length=20, choices=TAX_CHOICES, default="Inclusive")
    tax_value = models.ForeignKey(Tax, on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.mrp <= 0:
            raise ValueError("MRP must be greater than 0")
        
        # Calculate selling price based on MRP and discount
        if self.discount_price > 0:
            self.price = self.mrp - (self.mrp * Decimal(self.discount_price) / 100)
        else:
            self.price = self.mrp

        # Calculate tax amounts
        if self.tax_value:
            tax_rate = Decimal(self.tax_value.tax_percentage) / 100
            if self.tax == "Exclusive":
                self.tax_amount = round(self.price * tax_rate, 2)
                self.price_before_tax = round(self.price, 2)
                self.price = round(self.price + self.tax_amount, 2)
            elif self.tax == "Inclusive":
                self.price_before_tax = round(self.price / (1 + tax_rate), 2)
                self.tax_amount = round(self.price - self.price_before_tax, 2)
        else:
            self.price_before_tax = round(self.price, 2)
            self.tax_amount = Decimal(0)

        # Generate product code if not set
        if not self.product_code:
            self.product_code = self.generate_serial_number()

        super(Product, self).save(*args, **kwargs)

    def generate_serial_number(self):
        prefix = "PR"
        while True:
            random_number = random.randint(1000, 9999)
            order_number = f"{prefix}-{random_number}"
            if not Product.objects.filter(product_code=order_number).exists():
                return order_number
            
    def get_approved_reviews(self):
        """Returns only approved reviews for this product"""
        return self.reviews.all()
    
    def get_rating_summary(self):
        """Returns the rating summary for this product"""
        try:
            return self.rating_summary
        except:
            return None

    def __str__(self):
        return self.name + " " + str(self.brand)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    is_primary = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {'Primary' if self.is_primary else 'Secondary'}"
    
class ProductVideo(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='product_videos/')

    def __str__(self):
        return f"{self.product.name} - Video"
    
    
class ProductAttributeCategory(models.Model):
    """
    Represents categories like "Specification", "Connectivity", "Case".
    """
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class ProductAttribute(models.Model):
    """
    Represents attributes like "RAM", "Storage", "Year", "HDMI", etc.
    """
    category = models.ForeignKey(ProductAttributeCategory, on_delete=models.CASCADE, related_name="attributes")
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.category.name} - {self.name}"
    



class ProductAttributeValue(models.Model):
    """
    Represents values for attributes, which can be text, numbers, or lists.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="attributes")
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE, related_name="values")  # Use JSONField to store lists, numbers, or text dynamically

    def __str__(self):
        return f"{self.product.name} - {self.attribute.name}: {self.value}"



class AttributeValueDetail(models.Model):
    """
    Stores individual values for a ProductAttributeValue.
    """
    attribute_value = models.ForeignKey(ProductAttributeValue, on_delete=models.CASCADE, related_name="details")
    value = models.CharField(max_length=255)

    def __str__(self):
        return self.value
    

class VariantRelationshipAttribute(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name
    
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variant_parent")
    variant_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variant_item")
    relationship = models.ForeignKey(VariantRelationshipAttribute, on_delete=models.CASCADE)
    relationship_value = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.product} -> {self.variant_product} ({self.relationship_value})"
    


    
#pairing models best paired with 


from django.core.validators import MinValueValidator, MaxValueValidator

class ProductPairing(models.Model):
    """
    Model for storing product pairings (products that go well together)
    """
    primary_product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='paired_products')
    paired_product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='paired_with')
    pairing_strength = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1-5 indicating how strongly these products pair together"
    )
    description = models.TextField(
        blank=True, 
        null=True, 
        help_text="Optional description explaining why these products work well together"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('primary_product', 'paired_product')
        ordering = ['-pairing_strength', '-created_at']

    def __str__(self):
        return f"{self.primary_product.name} paired with {self.paired_product.name}"
    

# recommendation for product 


from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class ProductView(models.Model):
    """Track when users view products"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    session_id = models.CharField(max_length=100, null=True, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['product']),
            models.Index(fields=['session_id']),
        ]
    
    @classmethod
    def record_view(cls, product, user=None, session_id=None):
        """Record that a product was viewed"""
        return cls.objects.create(
            product=product,
            user=user,
            session_id=session_id
        )
    
    @classmethod
    def get_recently_viewed(cls, user=None, session_id=None, limit=10):
        """Get recently viewed products for a user or session"""
        query = cls.objects.all()
        if user:
            query = query.filter(user=user)
        elif session_id:
            query = query.filter(session_id=session_id)
        else:
            return []
            
        # Get distinct products, ordered by most recent view
        viewed_products = query.order_by('-viewed_at').distinct('product')[:limit]
        return [view.product for view in viewed_products]
        
    def __str__(self):
        user_str = str(self.user) if self.user else self.session_id
        return f"{user_str} viewed {self.product.name}"


class ProductRecommendation(models.Model):
    """Model for storing pre-calculated product recommendations"""
    RECOMMENDATION_TYPES = (
        ('similar', 'Similar Products'),
        ('frequently_bought', 'Frequently Bought Together'),
        ('popular_in_category', 'Popular in Category'),
        ('trending', 'Trending Now'),
        ('custom', 'Custom Recommendation')
    )
    
    source_product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='recommendations')
    recommended_product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='recommended_for')
    recommendation_type = models.CharField(max_length=30, choices=RECOMMENDATION_TYPES)
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('source_product', 'recommended_product', 'recommendation_type')
        ordering = ['-score']
        indexes = [
            models.Index(fields=['source_product', 'recommendation_type', '-score']),
        ]
        
    def __str__(self):
        return f"{self.get_recommendation_type_display()}: {self.source_product.name} → {self.recommended_product.name}"
    



# featured product modeling

class FeaturedProducts(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    featured_name = models.CharField(max_length=50, help_text="eg . FPS MONGER") 
    tagline = models.CharField(max_length=100)
    cpu  = models.CharField(max_length=50)
    cpu_clock = models.CharField(max_length=100)
    gpu = models.CharField(max_length=200)
    gpu_vram = models.CharField(max_length=200)
    ram = models.CharField(max_length=200)
    storage = models.CharField(max_length=200)
    banner_image = models.ImageField(upload_to="feature_product_image")
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=True)

    def __str__(self):
        return str(self.product.name) + " " + str(self.featured_name)
