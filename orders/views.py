from rest_framework.decorators import api_view, permission_classes


# This module provides views for managing cart operations, order creation, and payment processing 
# in an e-commerce backend. It includes functionalities for authenticated and session-based users.
# Functions:
# ----------
# - add_to_cart(request):
#     Add an item to the cart. Authenticated users have personalized carts, while unauthenticated 
#     users use session-based carts.
# - cart_detail(request):
# - remove_from_cart(request):
#     Remove an item from the cart. Handles both authenticated and session-based carts.
# Classes:
# --------
# - IncreaseCartItemQuantityView(APIView):
#     Increase the quantity of a specific item in the cart.
# - DecreaseCartItemQuantityView(APIView):
#     Decrease the quantity of a specific item in the cart. If the quantity becomes zero, the item 
#     is removed from the cart.
# - CreateSingleProductOrderView(APIView):
#     Create an order for a single product. Validates stock availability and calculates total price, 
#     tax, and discounts. Integrates with Razorpay for payment processing.
# - PaymentCallbackView(APIView):
#     Handle Razorpay payment callback. Verifies payment signature and updates the order's payment 
#     and order status.
# - create_cart_order(request):
#     Create an order for all items in the user's cart. Validates stock availability for all items, 
#     calculates totals, and integrates with Razorpay for payment processing.
# Notes:
# ------
# - The module uses Django REST Framework (DRF) for API views and serializers.
# - Razorpay is used for payment integration.
# - The `DeliveryAddress` model is used to associate orders with a delivery address.
# - The `Cart`, `CartItem`, `Product`, `Order`, and `OrderItem` models are used to manage cart 
#   and order data.
# TODO:
# -----
# - Add functionality for handling product reviews and ratings.



from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status

import json
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Cart, CartItem, Product,OrderItem, Order
from .serializers import CartSerializer, CartItemSerializer
from home.models import DeliveryAddress


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
    """
    Handles the removal of an item from the user's cart.
    This function checks if the user is authenticated. If authenticated, it retrieves the cart associated
    with the user. If not authenticated, it retrieves the cart associated with the session key. The function
    then attempts to remove the specified item from the cart.
    Parameters:
        request (HttpRequest): The HTTP request object containing user authentication and data payload.
    Returns:
        Response: A JSON response containing:
            - "data": Serialized cart data after the operation.
            - "message": Success message if the item is removed.
            - "error": Error message if the item is not found or the cart is empty.
            - HTTP Status Codes:
                - 200 OK: If the item is successfully removed.
                - 404 NOT FOUND: If the cart is empty or the item is not found.
            item_id = ('item_id') is the parameter to remove
                
    """
   

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


class IncreaseCartItemQuantityView(APIView):
    def post(self, request, cart_id, product_id):
        try:
            cart = Cart.objects.get(id=cart_id)
            product = Product.objects.get(id=product_id)
            
            # First check if the item exists
            try:
                cart_item = CartItem.objects.get(cart=cart, product=product)
                cart_item.quantity += 1
                cart_item.save()
            except CartItem.DoesNotExist:
                # Create new cart item with price set
                cart_item = CartItem.objects.create(
                    cart=cart,
                    product=product,
                    quantity=1,
                    price=product.price
                )
            
            # Serialize the cart after modifications
            cartserializer = CartSerializer(instance=cart)
            
            return Response(cartserializer.data, status=status.HTTP_200_OK)
            
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        

        
class DecreaseCartItemQuantityView(APIView):
    def post(self, request, cart_id, product_id):
        try:
            cart = Cart.objects.get(id=cart_id)
            cartserializer = CartSerializer(instance = cart)
            product = Product.objects.get(id=product_id)
            cart_item = CartItem.objects.get(cart=cart, product=product)

            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
                cartserializer = CartSerializer(instance = cart)

                return Response(cartserializer.data, status=status.HTTP_200_OK)
            else:
                cart_item.delete()
                return Response({"message": "Item removed from cart"}, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        except CartItem.DoesNotExist:
            return Response({"error": "Item not found in cart"}, status=status.HTTP_404_NOT_FOUND)
        

# order creation and functionalities


from django.db import transaction
import razorpay
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

class CreateSingleProductOrderView(APIView):
    def post(self, request):
        user = request.user
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        delivery_address_id = request.data.get("delivery_address_id")
        if not delivery_address_id:
            return Response({"error": "Delivery address is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            delivery_address = DeliveryAddress.objects.get(id=delivery_address_id, user=user)
        except DeliveryAddress.DoesNotExist:
            return Response({"error": "Invalid delivery address"}, status=status.HTTP_400_BAD_REQUEST)


        try:
            product = Product.objects.get(id=product_id)

            # Check if stock is sufficient
            if product.stock < quantity:
                return Response(
                    {"error": f"Insufficient stock for product: {product.name}. Available: {product.stock}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Calculate total price
            total_price = product.price * quantity

            # Create Order
            order = Order.objects.create(
                user=user,
                total_price=total_price,
                total_tax=product.tax_amount * quantity,
                price_before_tax=product.price_before_tax * quantity,
                total_discount=(product.mrp - product.price) * quantity,
                delivery_address = delivery_address
            )

            # Create OrderItem
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price,
                total_price=product.price * quantity,
                product_discount=(product.mrp - product.price) * quantity,
                total_tax=product.tax_amount * quantity,
                price_after_tax=(product.price + product.tax_amount) * quantity
            )

            # Reduce stock
            product.stock -= quantity
            product.save()
            order.save()
            data = {
                "amount": order.total_price * 100,
                "currency": "INR",
                "payment_capture": "1"
            }
            raz_order = razorpay_client.order.create(data)
            order.payment_order_id = raz_order["id"]
            order.save()

            return Response({"order_id": order.id, "total_price": total_price}, status=status.HTTP_201_CREATED)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_cart_order(request):
    user = request.user
    delivery_address_id = request.data.get("delivery_address_id")

    try:
        cart = get_object_or_404(Cart, user=user)
        cart_items = cart.items.all()

        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
        if not delivery_address_id:
            return Response({"error": "Delivery address is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            delivery_address = DeliveryAddress.objects.get(id=delivery_address_id, user=user)
        except DeliveryAddress.DoesNotExist:
            return Response({"error": "Invalid delivery address"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # Check stock for all cart items
            for item in cart_items:
                if item.product.stock < item.quantity:
                    return Response(
                        {"error": f"Insufficient stock for product: {item.product.name}. Available: {item.product.stock}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Calculate totals
            # total_price = sum(item.quantity * item.price for item in cart_items)
            # total_tax = sum(item.quantity * item.product.tax_amount for item in cart_items)
            # total_discount = sum((item.product.mrp - item.product.price) * item.quantity for item in cart_items)

            # Create the order
            order = Order.objects.create(
                user=user,
                total_price=0,
                total_tax=0,
                price_before_tax=0 ,
                total_discount=0,
                delivery_address = delivery_address
            )
            order.save()

            # Create order items and update product stock
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.price,
                    total_price=item.quantity * item.price,
                    product_discount=(item.product.mrp - item.product.price) * item.quantity,
                    total_tax=item.product.tax_amount * item.quantity,
                    price_after_tax=(item.price + item.product.tax_amount) * item.quantity
                )

                # Reduce product stock
                item.product.stock -= item.quantity
                item.product.save()

            # Clear cart
            cart_items.delete()
            data = {
                "amount": order.total_price * 100,
                "currency": "INR",
                "payment_capture": "1"
            }
            raz_order = razorpay_client.order.create(data)
            order.payment_order_id = raz_order["id"]
            order.save()

        return Response({"order_id": order.id, "total_price": order.total_price}, status=status.HTTP_201_CREATED)

    except Cart.DoesNotExist:
        return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)

        


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import razorpay
from .models import Order

class PaymentCallbackView(APIView):
    def post(self, request):
        response_data = request.data  # Use request.data instead of request.POST
        order_id = response_data.get("razorpay_order_id")
        payment_id = response_data.get("razorpay_payment_id")
        signature = response_data.get("razorpay_signature")
        payment_status = response_data.get("payment_status")

        # Validate required fields
        if not order_id or not payment_id or not signature:
            return Response({"error": "Missing required payment details"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(payment_order_id=order_id)

            # Verify Razorpay signature
            try:
                razorpay_client.utility.verify_payment_signature(response_data)
            except razorpay.errors.SignatureVerificationError:
                return Response({"error": "Invalid payment signature"}, status=status.HTTP_400_BAD_REQUEST)

            # Update order status based on Razorpay's response
            if payment_status == 'SUCCESS':
                order.order_status = 'PAID'
                order.payment_status = 'SUCCESS'
            else:
                order.payment_status = 'FAILED'

            order.save()
            return Response({"message": "Payment status updated"}, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)






### Reviews and rating Added 


###----------------------------------------------------------------###----------------------------------------------------------------###----------------------------------------------------------------
###----------------------------------------------------------------###----------------------------------------------------------------###----------------------------------------------------------------
###----------------------------------------------------------------###----------------------------------------------------------------###----------------------------------------------------------------
###----------------------------------------------------------------###----------------------------------------------------------------###----------------------------------------------------------------
