from django.urls import path 
from .import views 


urlpatterns = [
    path("add_to_cart/",views.add_to_cart,name="add_to_cart"),
    path("cart_detail/",views.cart_detail,name="cart_detail"),
    path("remove_from_cart/",views.remove_from_cart,name="remove_from_cart")
]