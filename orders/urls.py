from django.urls import path 
from .import views 


urlpatterns = [
    path("add_to_cart/",views.add_to_cart,name="add_to_cart"),
    path("cart_detail/",views.cart_detail,name="cart_detail"),
    path("remove_from_cart/",views.remove_from_cart,name="remove_from_cart"),
    path('cart/<int:cart_id>/product/<int:product_id>/increase/', views.IncreaseCartItemQuantityView.as_view(), name='increase-cart-item'),
    path('cart/<int:cart_id>/product/<int:product_id>/decrease/', views.DecreaseCartItemQuantityView.as_view(), name='decrease-cart-item'),

    # order
    path('order/single-product/', views.CreateSingleProductOrderView.as_view(), name='create-single-product-order'),
    path('order/cart/', views.create_cart_order, name='create-cart-order'),
    path('payment/callback/', views.PaymentCallbackView.as_view(), name='payment-callback'),
]