from django.urls import path
from . import views_testing, views

urlpatterns = [
    path('admin_board', views_testing.admin_board, name='admin_board'),
    path('add_tax/', views_testing.tax_add, name='tax_add'),
    path('add_category/', views_testing.category_add, name='category_add'),
    path('add_brand/', views_testing.brand_add, name='brand_add'),
    path('add_product/', views_testing.product_add, name='product_add'),
    path('add_product_image/', views_testing.product_image_add, name='product_image_add'),
    path('add_product_video/', views_testing.product_video_add, name='product_video_add'),
    path('product_view/', views_testing.product_view, name='product_view'),
    path("AddTax/", views_testing.AddTax, name="AddTax"),
    path("ListTax/", views_testing.ListTax, name="ListTax"),
    path("delete_tax/<int:pk>", views_testing.delete_tax, name="delete_tax"),
    path("tax_single_update/<int:pk>", views_testing.tax_single_update, name="tax_single_update"),

    path("list_products",views_testing.list_products,name="list_products"),
    path("add_category",views_testing.add_category,name="add_category"),
    path("add_product",views_testing.add_product,name="add_product"),
    path("product_update/<int:pk>",views_testing.product_update,name="product_update"),

    path("add_attribute_value_to_product/<int:pk>",views_testing.add_attribute_value_to_product,name="add_attribute_value_to_product"),
    path("View_product/<int:pk>",views_testing.View_product,name="View_product"),
    path("list_brand",views_testing.list_brand,name="list_brand"),


    # apis

    path("Products_view/",views.Products_view,name="Products_view"),
]
