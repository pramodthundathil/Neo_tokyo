from django.db import models
from inventory.models import Product

class ProductDropDownCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)  # For SEO-friendly URLs
    description = models.TextField(blank=True, null=True)  # Category description
    is_active = models.BooleanField(default=True)  # For enabling/disabling categories
    order = models.PositiveIntegerField(default=0)  # For custom ordering
    date_added = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Product Category"
        verbose_name_plural = "Product Categories"

    def __str__(self):
        return str(self.name)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class HeroCarousel(models.Model):
    dropdown_menu = models.ForeignKey(
        ProductDropDownCategory, 
        on_delete=models.CASCADE, 
        related_name="hero_carousels"  # Better naming
    )
    image = models.FileField(upload_to="carousel_images/")  # Better path structure
    alt_text = models.CharField(max_length=100, blank=True)  # For accessibility
    head_one = models.CharField(max_length=50)  # Increased length
    head_two = models.CharField(max_length=50)  # Increased length
    description = models.CharField(max_length=200)
    button_text = models.CharField(max_length=20, default="Shop Now")  # Call-to-action text
    button_link = models.URLField(blank=True, null=True)  # Optional link
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)  # For carousel ordering
    date_added = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)

    class Meta:
        ordering = ['order', '-date_added']
        verbose_name = "Hero Carousel"
        verbose_name_plural = "Hero Carousels"

    def __str__(self):
        return f"Hero Carousel - {self.dropdown_menu.name} ({self.head_one})"

class ProductSpecificationDescription(models.Model):
    dropdown_menu = models.ForeignKey(
        ProductDropDownCategory, 
        on_delete=models.CASCADE, 
        related_name="specifications"
    )
    title = models.CharField(max_length=100)  # Increased length
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)  # For custom ordering
    is_active = models.BooleanField(default=True)
    date_added = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)

    class Meta:
        ordering = ['order', 'title']
        verbose_name = "Product Specification"
        verbose_name_plural = "Product Specifications"

    def __str__(self):
        return f"{self.dropdown_menu.name} - {self.title}"

class ProductListOnProduct(models.Model):
    dropdown_menu = models.ForeignKey(
        ProductDropDownCategory, 
        on_delete=models.CASCADE, 
        related_name="category_products"
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name="product_categories"
    )
    is_featured = models.BooleanField(default=False)  # Featured products
    order = models.PositiveIntegerField(default=0)  # Custom ordering within category
    date_added = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-date_added']
        unique_together = ['dropdown_menu', 'product']  # Prevent duplicates
        verbose_name = "Category Product"
        verbose_name_plural = "Category Products"

    def __str__(self):
        return f"{self.dropdown_menu.name} - {self.product.name}"