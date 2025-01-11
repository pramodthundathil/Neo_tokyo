from django.urls import path
from . import views_testing, views

urlpatterns = [
    path('', views_testing.admin_board, name='admin_board'),
    path('add_tax/', views_testing.tax_add, name='tax_add'),
    path('add_category/', views_testing.category_add, name='category_add'),
    path('add_brand/', views_testing.brand_add, name='brand_add'),
    path('add_product/', views_testing.product_add, name='product_add'),
    path('add_product_image/', views_testing.product_image_add, name='product_image_add'),
    path('add_product_video/', views_testing.product_video_add, name='product_video_add'),
    path('add_attribute/', views_testing.attribute_add, name='attribute_add'),
    path('add_product_spec/', views_testing.product_spec_add, name='product_spec_add'),
    path('add_product_variant/', views_testing.product_variant_add, name='product_variant_add'),



    # apis

    path("Products_view/",views.Products_view,name="Products_view"),
]
