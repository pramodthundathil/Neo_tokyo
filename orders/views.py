from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status
from .models import Cart, CartItem, Product
from .serializers import CartSerializer, CartItemSerializer
import json
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


@swagger_auto_schema(
    method='post', 
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'product_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, default=1),
        },
    )
)
@api_view(['POST'])
@permission_classes([IsAuthenticatedOrReadOnly])  # Allow authenticated users and read-only for others
def add_to_cart(request):
    """
    Add an item to the cart. Authenticated users have personalized carts,
    while unauthenticated users use session-based carts.
    """
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity', 1)

    try:
        # Validate product existence
        product = Product.objects.filter(id=product_id).first()
        if not product:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        # Get or create a cart
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            session_key = request.session.session_key or request.session.create()
            cart, created = Cart.objects.get_or_create(session_key=session_key)

        # Add or update cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, 
            product=product, 
            defaults={'price': product.price}
        )
        if not created:
            cart_item.quantity += int(quantity)
        cart_item.save()

        return Response({"message": "Item added to cart."}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    



@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])  # Authenticated users and session-based carts for guests
def cart_detail(request):
    """
    Retrieve the details of the user's cart or session-based cart.
    """
    # Check if the user is authenticated or session-based
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    else:
        session_key = request.session.session_key
        if not session_key:
            return Response({"message": "Cart is empty."}, status=status.HTTP_404_NOT_FOUND)
        cart = Cart.objects.filter(session_key=session_key).first()

    if not cart:
        return Response({"message": "Cart is empty."}, status=status.HTTP_404_NOT_FOUND)

    serializer = CartSerializer(cart)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def remove_from_cart(request):
    item_id = request.data.get('item_id')
    cart_item = CartItem.objects.filter(id=item_id).first()

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    else:
        session_key = request.session.session_key
        if not session_key:
            return Response({"message": "Cart is empty."}, status=status.HTTP_404_NOT_FOUND)
        cart = Cart.objects.filter(session_key=session_key).first()
    
    cart_serializer = CartSerializer(instance = cart)

    if not cart_item:
        return Response({"data":cart_serializer.data, "error": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)

    cart_item.delete()
    return Response({"data":cart_serializer.data,"message": "Item removed from cart."}, status=status.HTTP_200_OK)
