from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from home.views import IsAdmin 

from .models import (
    ProductDropDownCategory, HeroCarousel, 
    ProductSpecificationDescription, ProductListOnProduct
)
from .serializers import (
    ProductDropDownCategoryListSerializer,
    ProductDropDownCategoryDetailSerializer,
    HeroCarouselSerializer,
    HeroCarouselCreateSerializer,
    ProductSpecificationDescriptionSerializer,
    ProductSpecificationDescriptionCreateSerializer,
    ProductListOnProductSerializer,
    ProductListOnProductCreateSerializer
)


class ProductDropDownCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product categories
    """
    queryset = ProductDropDownCategory.objects.filter(is_active=True)
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductDropDownCategoryListSerializer
        return ProductDropDownCategoryDetailSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'page_data', 'featured_products']:
            return [permissions.AllowAny()]
        return [IsAdmin()]
    
    def get_queryset(self):
        if self.action == 'retrieve':
            # Optimize queries with prefetch_related for detail view
            return ProductDropDownCategory.objects.filter(is_active=True).prefetch_related(
                Prefetch('hero_carousels', queryset=HeroCarousel.objects.filter(is_active=True)),
                Prefetch('specifications', queryset=ProductSpecificationDescription.objects.filter(is_active=True)),
                Prefetch('category_products', queryset=ProductListOnProduct.objects.select_related('product')),
            )
        return ProductDropDownCategory.objects.filter(is_active=True)
    
    @action(detail=True, methods=['get'], url_path='page-data')
    def page_data(self, request, slug=None):
        """
        Get complete category page data in a single API call
        Optimized for frontend consumption
        """
        try:
            category = ProductDropDownCategory.objects.prefetch_related(
                Prefetch('hero_carousels', queryset=HeroCarousel.objects.filter(is_active=True)),
                Prefetch('specifications', queryset=ProductSpecificationDescription.objects.filter(is_active=True)),
                Prefetch('category_products', queryset=ProductListOnProduct.objects.select_related('product__brand')),
            ).get(slug=slug, is_active=True)
            
            serializer = ProductDropDownCategoryDetailSerializer(category)
            return Response(serializer.data)
            
        except ProductDropDownCategory.DoesNotExist:
            return Response(
                {'error': 'Category not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'], url_path='featured-products')
    def featured_products(self, request, slug=None):
        """Get only featured products for a category"""
        try:
            category = get_object_or_404(ProductDropDownCategory, slug=slug, is_active=True)
            featured_products = ProductListOnProduct.objects.filter(
                dropdown_menu=category,
                is_featured=True
            ).select_related('product')
            
            serializer = ProductListOnProductSerializer(featured_products, many=True)
            return Response(serializer.data)
            
        except ProductDropDownCategory.DoesNotExist:
            return Response(
                {'error': 'Category not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class HeroCarouselViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing hero carousel items
    """
    queryset = HeroCarousel.objects.filter(is_active=True)
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return HeroCarouselCreateSerializer
        return HeroCarouselSerializer
    
    def get_permissions(self):
        if self.action == 'list':
            return [permissions.AllowAny()]
        return [IsAdmin()]
    
    def get_queryset(self):
        queryset = HeroCarousel.objects.filter(is_active=True)
        category_slug = self.request.query_params.get('category', None)
        
        if category_slug:
            queryset = queryset.filter(
                dropdown_menu__slug=category_slug
            ).select_related('dropdown_menu')
        
        return queryset


class ProductSpecificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product specifications
    """
    queryset = ProductSpecificationDescription.objects.filter(is_active=True)
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProductSpecificationDescriptionCreateSerializer
        return ProductSpecificationDescriptionSerializer
    
    def get_permissions(self):
        if self.action == 'list':
            return [permissions.AllowAny()]
        return [IsAdmin()]
    
    def get_queryset(self):
        queryset = ProductSpecificationDescription.objects.filter(is_active=True)
        category_slug = self.request.query_params.get('category', None)
        
        if category_slug:
            queryset = queryset.filter(dropdown_menu__slug=category_slug)
        
        return queryset


class CategoryProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing category-product relationships
    """
    queryset = ProductListOnProduct.objects.all()
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProductListOnProductCreateSerializer
        return ProductListOnProductSerializer
    
    def get_permissions(self):
        if self.action == 'list':
            return [permissions.AllowAny()]
        return [IsAdmin()]
    
    def get_queryset(self):
        queryset = ProductListOnProduct.objects.select_related('product', 'dropdown_menu')
        category_slug = self.request.query_params.get('category', None)
        
        if category_slug:
            queryset = queryset.filter(dropdown_menu__slug=category_slug)
        
        return queryset