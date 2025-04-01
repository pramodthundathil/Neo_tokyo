from rest_framework import viewsets, permissions, status, generics, filters
from rest_framework.response import Response
from rest_framework.decorators import action
# from django_filters.rest_framework import DjangoFilterBackend
from inventory.models import  Product
from .models import Review
from .serializers import ReviewSerializer, ProductReviewSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from home.views import IsAdmin 
from .permissions import IsOwnerOrReadOnly
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from orders.models import Order


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [ filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product', 'rating', 'is_verified_purchase', 'is_approved']
    search_fields = ['title', 'comment']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Review.objects.all()
        # Non-staff users can only see approved reviews
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_approved=True)
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        review = self.get_object()
        review.is_approved = True
        review.save()
        return Response({'status': 'review approved'})
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def reject(self, request, pk=None):
        review = self.get_object()
        review.is_approved = False
        review.save()
        return Response({'status': 'review rejected'})


class ProductReviewsView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductReviewSerializer
    permission_classes = [AllowAny]


# reviews and Rating Add 

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_product_review(request):
    """
    Endpoint for users to submit a product review
    
    Required fields in request data:
    - product_id (int): ID of the product to review
    - rating (int): Rating from 1-5
    - title (str): Review title
    - comment (str): Detailed review comment
    - images (list, optional): Images to attach to the review
    """
    product_id = request.data.get('product_id')
    product = get_object_or_404(Product, id=product_id)
    
    # Check if user already reviewed this product
    if Review.objects.filter(user=request.user, product=product).exists():
        return Response(
            {"detail": "You have already reviewed this product. You can edit your existing review instead."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Prepare review data
    review_data = {
        'product': product.id,
        'rating': request.data.get('rating'),
        'title': request.data.get('title'),
        'comment': request.data.get('comment'),
    }
    
    # Handle image uploads if any
    uploaded_images = request.FILES.getlist('images', [])
    if uploaded_images:
        review_data['uploaded_images'] = uploaded_images
    
    # Create serializer with review data
    serializer = ReviewSerializer(data=review_data, context={'request': request})
    
    if serializer.is_valid():
        review = serializer.save(user=request.user)
        
        # Check if the user has purchased this product
        # This is a placeholder - implement your actual verification logic
        if Order.objects.filter(user=request.user, items__product=product).exists():
            review.is_verified_purchase = True
            review.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_product_review(request, review_id):
    """
    Endpoint for users to update their existing product review
    
    Path parameter:
    - review_id (int): ID of the review to update
    
    Optional fields in request data:
    - rating (int): Updated rating from 1-5
    - title (str): Updated review title
    - comment (str): Updated review comment
    - images (list, optional): New images to attach to the review
    """
    # Get review and validate ownership
    review = get_object_or_404(Review, id=review_id)
    if review.user != request.user:
        return Response(
            {"detail": "You do not have permission to edit this review."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Prepare update data
    update_data = {}
    for field in ['rating', 'title', 'comment']:
        if field in request.data:
            update_data[field] = request.data.get(field)
    
    # Handle image uploads if any
    uploaded_images = request.FILES.getlist('images', [])
    if uploaded_images:
        update_data['uploaded_images'] = uploaded_images
    
    # Update review
    serializer = ReviewSerializer(review, data=update_data, partial=True, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_product_review(request, review_id):
    """
    Endpoint for users to delete their own review
    
    Path parameter:
    - review_id (int): ID of the review to delete
    """
    review = get_object_or_404(Review, id=review_id)
    if review.user != request.user:
        return Response(
            {"detail": "You do not have permission to delete this review."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    review.delete()
    return Response({"detail": "Review successfully deleted."}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_reviews(request):
    """
    Endpoint for users to retrieve all their own reviews
    """
    reviews = Review.objects.filter(user=request.user).order_by('-created_at')
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_product_reviews(request):
    """
    Endpoint for users to retrieve all Product reviews
    """
    product_id = request.data.get('product_id')
    reviews = Review.objects.filter(product_id=product_id).order_by('-created_at')
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)






