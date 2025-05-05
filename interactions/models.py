from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg
from inventory.models import Product
from django.utils.crypto import get_random_string

User = get_user_model()

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_reviews')
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5"
    )
    title = models.CharField(max_length=100)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ('product', 'user')  # One review per user per product
    
    def __str__(self):
        return f"{self.user.username}'s review on {self.product.name}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update product average rating
        avg_rating = Review.objects.filter(
            product=self.product, 
            is_approved=True
        ).aggregate(Avg('rating'))['rating__avg'] or 0
        
        # Update or create ProductRatingSummary
        summary, created = ProductRatingSummary.objects.get_or_create(
            product=self.product,
            defaults={'average_rating': avg_rating}
        )
        if not created:
            summary.average_rating = avg_rating
            summary.save()


class ReviewImage(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='review_images/')
    
    def __str__(self):
        return f"Image for {self.review}"


class ProductRatingSummary(models.Model):
    """Stores aggregated rating data for quick access"""
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='rating_summary')
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    
    # Rating distribution
    five_star_count = models.PositiveIntegerField(default=0)
    four_star_count = models.PositiveIntegerField(default=0)
    three_star_count = models.PositiveIntegerField(default=0)
    two_star_count = models.PositiveIntegerField(default=0)
    one_star_count = models.PositiveIntegerField(default=0)
    
    def update_counts(self):
        """Update rating distribution counts"""
        approved_reviews = Review.objects.filter(product=self.product, is_approved=True)
        self.total_reviews = approved_reviews.count()
        self.five_star_count = approved_reviews.filter(rating=5).count()
        self.four_star_count = approved_reviews.filter(rating=4).count()
        self.three_star_count = approved_reviews.filter(rating=3).count()
        self.two_star_count = approved_reviews.filter(rating=2).count()
        self.one_star_count = approved_reviews.filter(rating=1).count()
        self.save()
    
    def __str__(self):
        return f"Rating summary for {self.product.name}: {self.average_rating}/5"


class GrievanceTicket(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tickets')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='grivience_on_product')
    product_name = models.CharField(max_length=255, null=True, blank=True)

    image = models.FileField(upload_to="grievance_image", null=True, blank=True)
    link  = models.URLField(null=True, blank=True)

    product_serial_number = models.CharField(max_length=100, null=True, blank=True)
    grievance =  models.TextField()
    conclusion = models.TextField(null=True, blank=True)
    ticket_id = models.CharField(max_length=100)
    is_concluded = models.BooleanField(default=False)

    def generate_unique_ticket_id():
        while True:
            ticket_id = get_random_string(length=10, allowed_chars='0123456789')
            if not GrievanceTicket.objects.filter(ticket_id=ticket_id).exists():
                return ticket_id

    def save(self, *args, **kwargs):
        if not self.ticket_id:
            self.ticket_id = self.generate_unique_ticket_id()
        super().save(*args, **kwargs)

    
    def __str__(self):
        """Generate a string with user details for the grievance ticket."""
        user_info = f"User: {self.user.username} (ID: {self.user.id})"
        product_info = f"Product: {self.product.name if self.product else 'N/A'}"
        serial_info = f"Serial Number: {self.product_serial_number if self.product_serial_number else 'N/A'}"

        return f"{user_info}, {product_info}, {serial_info}"

