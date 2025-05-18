from django.urls import path
from . import views_testing, views

from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, TaxViewSet, BrandViewSet,
    ProductAttributeCategorySerializerViewSet, 
    ProductAttributeViewSet, ProductAttributeValueViewSet,
    AttributeValueDetailViewSet,
    VariantRelationshipAttributeViewSet,
    ProductVariantViewSet,
    ProductViewSet,
    ProductMediaViewSet,
    )

router = DefaultRouter()




urlpatterns = [

    #=====================================================================================================

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
    path("add_variant/<int:pk>",views_testing.add_variant,name="add_variant"),
    #=====================================================================================================

    


  
    #=====================================================================================================
    # apis
    #=====================================================================================================
    #=====================================================================================================
   
    # products 
    path("Products_view/",views.Products_view,name="Products_view"),
    path("Products_view_single/<int:pk>",views.Products_view_single,name="Products_view_single"),
    #=====================================================================================================

    #tax model 

    path("tax_view",views.tax_view,name="tax_view"),
    path("tax_add",views.tax_add,name="tax_add"),
    path("tax_single_view/<int:pk>",views.tax_single_view,name="tax_single_view"),
    path("tax_update/<int:pk>",views.tax_update,name="tax_update"),
    path("tax_delete/<int:pk>",views.tax_delete,name="tax_delete"),

    #=====================================================================================================

    # Category Models

    path("view_category",views.view_category,name="view_category"),
    path("category_single_view/<int:pk>",views.category_single_view,name="category_single_view"),
    path("category_add",views.category_add,name="category_add"),
    path("category_update/<int:pk>",views.category_update,name="category_update"),
    path("category_delete/<int:pk>",views.category_delete,name="category_delete"),
    path("ProductAttributeCategoryListView",views.ProductAttributeCategoryListView.as_view(),name="ProductAttributeCategoryListView"),
    path("view_category_allow_any/",views.view_category_allow_any,name="view_category_allow_any"),
    path("category_single_view_allow_any/<int:pk>",views.category_single_view_allow_any,name="category_single_view_allow_any"),

    #brand allow any serialization api end points ..........................................

    path("view_brand_allow_any/",views.view_brand_allow_any,name="view_brand_allow_any"),
    path("brands_single_view_allow_any/<int:pk>",views.brands_single_view_allow_any,name="brands_single_view_allow_any"),


    #=====================================================================================================
    ## product pairing 
    path('products/<str:pk>/with-pairings/', views.ProductWithPairingsView.as_view(), name='product-with-pairings'),
    path('products/<str:pk>/recommendations/', views.ProductWithPairingsView.as_view(), name='product-recommendations'),
    path('customer/purchased-products/', views.CustomerPurchasedProductsView.as_view(), name='customer-purchased-products'),

    #driver updates 
    path('products/<int:product_id>/updates/', 
         views.SingleProductDriverUpdatesView.as_view({'get': 'list'}), 
         name='product-updates'),

]


router.register(r'categories', CategoryViewSet, basename='categories')
router.register(r'taxes', TaxViewSet, basename='taxes')
router.register(r'brands', BrandViewSet, basename='brands'),
router.register(r'productattribute_category', ProductAttributeCategorySerializerViewSet, basename='productattribute_category'),
router.register(r'productattribute', ProductAttributeViewSet, basename='productattribute'),
router.register(r'productattribute_value', ProductAttributeValueViewSet, basename='productattribute_value'),
router.register(r'productattribute_details', AttributeValueDetailViewSet, basename='productattribute_details'),
router.register(r'variant_relationship', VariantRelationshipAttributeViewSet, basename='variant_relationship'),
router.register(r'product_variant', ProductVariantViewSet, basename='product_variant'),
router.register(r'product_admin', ProductViewSet, basename="product_admin")
router.register(r'products', ProductMediaViewSet, basename='product-media')
router.register(r'product-pairings', views.ProductPairingViewSet, basename="product_pairing")
router.register(r'recommendations', views.ProductRecommendationViewSet, basename="product_recommendation")
router.register(r'featured-products', views.FeaturedProductViewSet, basename='featured-products')
router.register(r'admin/product-updates', views.AdminProductUpdateViewSet, basename='admin-product-updates')
router.register(r'product-updates', views.CustomerProductUpdateViewSet, basename='product-updates')
router.register(r'update-notifications', views.ProductUpdateNotificationViewSet, basename='update-notifications')


urlpatterns += router.urls

