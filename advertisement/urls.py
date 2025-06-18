from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'categories', views.ProductDropDownCategoryViewSet, basename='category')
router.register(r'hero-carousels', views.HeroCarouselViewSet, basename='hero-carousel')
router.register(r'specifications', views.ProductSpecificationViewSet, basename='specification')
router.register(r'category-products', views.CategoryProductViewSet, basename='category-product')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('product/', include(router.urls)),
]

# This will generate the following URLs:
# 
# Categories:
# GET    /api/categories/                              - List all categories
# POST   /api/categories/                              - Create new category (admin only)
# GET    /api/categories/{slug}/                       - Get category detail
# PUT    /api/categories/{slug}/                       - Update category (admin only)
# PATCH  /api/categories/{slug}/                       - Partial update category (admin only)
# DELETE /api/categories/{slug}/                       - Delete category (admin only)
# GET    /api/categories/{slug}/page-data/             - Get complete category page data
# GET    /api/categories/{slug}/featured-products/     - Get featured products for category
#
# Hero Carousels:
# GET    /api/hero-carousels/                          - List all carousels (filter by ?category=slug)
# POST   /api/hero-carousels/                          - Create new carousel (admin only)
# GET    /api/hero-carousels/{id}/                     - Get carousel detail (admin only)
# PUT    /api/hero-carousels/{id}/                     - Update carousel (admin only)
# PATCH  /api/hero-carousels/{id}/                     - Partial update carousel (admin only)
# DELETE /api/hero-carousels/{id}/                     - Delete carousel (admin only)
#
# Specifications:
# GET    /api/specifications/                          - List all specifications (filter by ?category=slug)
# POST   /api/specifications/                          - Create new specification (admin only)
# GET    /api/specifications/{id}/                     - Get specification detail (admin only)
# PUT    /api/specifications/{id}/                     - Update specification (admin only)
# PATCH  /api/specifications/{id}/                     - Partial update specification (admin only)
# DELETE /api/specifications/{id}/                     - Delete specification (admin only)
#
# Category Products:
# GET    /api/category-products/                       - List all category-product relationships (filter by ?category=slug)
# POST   /api/category-products/                       - Create new relationship (admin only)
# GET    /api/category-products/{id}/                  - Get relationship detail (admin only)
# PUT    /api/category-products/{id}/                  - Update relationship (admin only)
# PATCH  /api/category-products/{id}/                  - Partial update relationship (admin only)
# DELETE /api/category-products/{id}/                  - Delete relationship (admin only)