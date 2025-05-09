from django.shortcuts import render, redirect, get_object_or_404
import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from home.views import IsAdmin 
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
                    ProductImageSerializer,
                    ProductSerializer,

                    ProductVideoSerializer,
                    TaxSerializer,

                    CategorySerializer,
                    BrandSerializer,
                    
                    ProductAttributeSerializer,
                    ProductAttributeCategorySerializer,
                    ProductVariantSerializer,
                    ProductAttributeValueSerializer,
                    AttributeValueDetail,
                    AttributeValueDetailSerializer,
                    VariantRelationshipAttributeSerializer,
                    ProductAttributeCategorySerializerForSort

                )
from .models import (Product,
                      Category, 
                      Tax, 
                      ProductImage, 
                      ProductVideo, 
                      Brand,

                      ProductAttribute,
                      ProductAttributeCategory,
                      ProductAttributeValue,

                      ProductVariant,
                      VariantRelationshipAttribute)


from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.shortcuts import get_object_or_404
from django.core.cache import cache
from rest_framework_simplejwt.tokens import RefreshToken
import random
from django.conf import settings
from django.core.mail import send_mail,EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site

#for inventory documentation url 
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets




# product views serializers can get the response of all product details and single details 
# it will allow all users to access this data even guest user 
# example inventory JSON data is below
# 
'''
{
    "id": 3,
    "product_code": "PR-5231",
    "name": "DELL PC",
    "brand": "DELL",
    "description": "Dell Inspiron 15 3530 Laptop - Powerful 15.6 inch FHD (39.62cm) Display, Intel Core i7-1355U, 16 GB RAM, 512 GB SSD, Windows 11 Home, Platinum Silver, Thin and Light, Ideal for Data Mavens",
    "category": "Pre Bulid PC",
    "mrp": "89096.00",
    "price": "89096.00",
    "discount_price": "0.00",
    "stock": 11,
    "is_available": true,
    "price_before_tax": "75505.08",
    "tax_amount": "13590.92",
    "tax": "Inclusive",
    "tax_value": {
        "tax_name": "GST",
        "tax_percentage": 18.0
    },
    "youtube_url": "https://getbootstrap.com/docs/5.0/components/modal/",
    "broacher": "/media/product_broacher/product.png",
    "whats_inside": "1 laptop",
    "more_info": "https://www.dell.com/en-in/shop/cty/pdp/spd/latitude-14-5450-laptop/on002l5450043in9?tfcid=30223580&gacd=10415953-9027-5761040-297509714-0&dgc=PLA&gad_source=1&gclid=Cj0KCQiAkJO8BhCGARIsAMkswyip6dTWuK",
    "images": [
        {
            "id": 4,
            "image": "/media/product_images/dell.jpg",
            "is_primary": true
        },
        {
            "id": 5,
            "image": "/media/product_images/dell_spec.jpg",
            "is_primary": false
        }
    ],
    "videos": [
        {
            "id": 2,
            "video": "/media/product_videos/4114797-uhd_3840_2160_25fps_8OMZ4Po.mp4"
        }
    ],
    "attributes": [
        {
            "id": 1,
            "attribute": {
                "id": 1,
                "category": {
                    "id": 1,
                    "name": "Specifications"
                },
                "name": "Ram"
            },
            "details": [
                {
                    "id": 1,
                    "value": "16 GB"
                },
                {
                    "id": 2,
                    "value": "8 GB"
                }
            ]
        },
        {
            "id": 2,
            "attribute": {
                "id": 2,
                "category": {
                    "id": 1,
                    "name": "Specifications"
                },
                "name": "GRAPHICS"
            },
            "details": [
                {
                    "id": 4,
                    "value": "NIVIDIA"
                },
                {
                    "id": 5,
                    "value": "RTX $)&) Ti Super 16 GB"
                }
            ]
        },
        {
            "id": 3,
            "attribute": {
                "id": 3,
                "category": {
                    "id": 1,
                    "name": "Specifications"
                },
                "name": "PROCESSOR"
            },
            "details": [
                {
                    "id": 3,
                    "value": "Core i7 2.5 Ghz"
                }
            ]
        },
        {
            "id": 4,
            "attribute": {
                "id": 4,
                "category": {
                    "id": 2,
                    "name": "CONNECTVITY / PORTS"
                },
                "name": "MOTHERBOARD"
            },
            "details": [
                {
                    "id": 7,
                    "value": "MSI H510M-A Pro Motherboard"
                },
                {
                    "id": 9,
                    "value": "335x216x446mm"
                }
            ]
        },
        {
            "id": 5,
            "attribute": {
                "id": 7,
                "category": {
                    "id": 1,
                    "name": "Specifications"
                },
                "name": "STORAGE"
            },
            "details": [
                {
                    "id": 6,
                    "value": "SAMSUNG 980 Pro"
                }
            ]
        },
        {
            "id": 6,
            "attribute": {
                "id": 8,
                "category": {
                    "id": 3,
                    "name": "DIMENSIONS"
                },
                "name": "CASE"
            },
            "details": [
                {
                    "id": 8,
                    "value": "335x216x446mm"
                }
            ]
        }
    ],
    "variant_parent": [
        {
            "id": 1,
            "product": "DELL PC DELL",
            "variant_product": "Latitude 5450 Laptop DELL",
            "relationship": {
                "id": 0,
                "name": "RAM"
            },
            "relationship_value": "16 GB"
        },
        {
            "id": 2,
            "product": "DELL PC DELL",
            "variant_product": "Latitude 5450 Laptop DELL",
            "relationship": {
                "id": 0,
                "name": "RAM"
            },
            "relationship_value": "32 GB"
        }
    ],
    "created_at": "2025-01-12T22:49:07.516100+05:30",
    "updated_at": "2025-01-13T21:44:29.808932+05:30"
}
'''
#  


@api_view(['GET'])
@permission_classes([AllowAny])
def Products_view(request):
    products = Product.objects.all()
    
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def Products_view_single(request,pk):
    products = get_object_or_404(Product, id = pk)
    
    serializer = ProductSerializer(instance = products)
    return Response(serializer.data, status=status.HTTP_200_OK)


#end of product without permission
#=========================================================================================================
#=========================================================================================================
#=========================================================================================================
#=========================================================================================================


#=========================================================TAX DATA ENTERING START========================

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def tax_view(request):
    tax = Tax.objects.all()
    serializer = TaxSerializer(tax, many = True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def tax_single_view(request,pk):
    tax = get_object_or_404(Tax, id = pk)
    serializer = TaxSerializer(instance = tax)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdmin])
def tax_add(request):
    serializer = TaxSerializer(data = request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Tax Value added successfully!"},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated, IsAdmin])
def tax_update(request, pk):
    try:
        # Get the existing Tax instance by primary key (pk)
        tax_instance = Tax.objects.get(pk=pk)
    except Tax.DoesNotExist:
        return Response(
            {"error": "Tax record not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = TaxSerializer(tax_instance, data=request.data, partial=True) 
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Tax record updated successfully!"},
            status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdmin])
def tax_delete(request, pk):
    try:
        # Get the Tax instance by primary key (pk)
        tax_instance = Tax.objects.get(pk=pk)
    except Tax.DoesNotExist:
        return Response(
            {"error": "Tax record not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    # Delete the instance
    tax_instance.delete()
    return Response(
        {"message": "Tax record deleted successfully!"},
        status=status.HTTP_204_NO_CONTENT
    )



class TaxViewSet(viewsets.ModelViewSet):
    # The queryset defines the set of objects that will be retrieved by the viewset.
    queryset = Tax.objects.all()
    
    # This defines which serializer should be used to serialize and deserialize the data.
    serializer_class = TaxSerializer
    
    # This defines which permissions the user needs to access this view.
    permission_classes = [IsAuthenticated, IsAdmin]

    def create(self, request, *args, **kwargs):
        # Custom response for successful creation
        response = super().create(request, *args, **kwargs)
        return Response(
            {
                "message": "Tax created successfully!",
                "data": response.data,
            },
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        # Custom response for successful update
        response = super().update(request, *args, **kwargs)
        return Response(
            {
                "message": "Tax updated successfully!",
                "data": response.data,
            },
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        # Custom response for successful deletion
        super().destroy(request, *args, **kwargs)
        return Response(
            {
                "message": "Tax deleted successfully!",
            },
            status=status.HTTP_204_NO_CONTENT,
        )


#=========================================================TAX DATA ENTERING END==========================

#=========================================================================================================
#=========================================================================================================

#=========================================================CATEGORY ENTERING Start==========================

@swagger_auto_schema(methods=['get'],operation_description="Get a list of all categories")
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def view_category(request):
    category = Category.objects.all()
    serializer = CategorySerializer(category, many = True)
    return Response(serializer.data,status=status.HTTP_200_OK )


@swagger_auto_schema(methods=['get'],operation_description="Get a list of all categories allow for public access")
@api_view(['GET'])
@permission_classes([AllowAny])
def view_category_allow_any(request):
    category = Category.objects.all()
    serializer = CategorySerializer(category, many = True)
    return Response(serializer.data,status=status.HTTP_200_OK )


@swagger_auto_schema(methods=['get'],operation_description="Get a Single Instance categories for public access")
@api_view(['GET'])
@permission_classes([AllowAny])
def category_single_view_allow_any(request,pk):
    category = get_object_or_404(Category, id = pk)
    serializer = CategorySerializer(instance = category)
    return Response(serializer.data, status=status.HTTP_200_OK)




class ProductAttributeCategoryListView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    def get(self, request):
        categories = ProductAttributeCategory.objects.prefetch_related('attributes').all()
        serializer = ProductAttributeCategorySerializerForSort(categories, many=True)
        return Response(serializer.data)
    

@swagger_auto_schema(methods=['get'],operation_description="Get a Single Instance categories")
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def category_single_view(request,pk):
    category = get_object_or_404(Category, id = pk)
    serializer = CategorySerializer(instance = category)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(methods=['post'],operation_description="Add new categories")
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdmin])
def category_add(request):
    serializer = CategorySerializer(data = request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Category added successfully!"},
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(methods=['patch'],operation_description="Update a Single Instance category")
@api_view(['PATCH'])
@permission_classes([IsAuthenticated, IsAdmin])
def category_update(request, pk):
    try:
        # Get the existing Tax instance by primary key (pk)
        category_instance = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return Response(
            {"error": "Category record not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    serializer = CategorySerializer(category_instance, data=request.data, partial=True) 
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Category record updated successfully!"},
            status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(methods=['delete'],operation_description="Delete a Single Instance categories")
@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdmin])
def category_delete(request, pk):
    try:
        # Get the Tax instance by primary key (pk)
        category_instance = Category.objects.get(pk=pk)
    except category_instance.DoesNotExist:
        return Response(
            {"error": "Category record not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    # Delete the instance
    category_instance.delete()
    return Response(
        {"message": "Category record deleted successfully!"},
        status=status.HTTP_204_NO_CONTENT
    )



class CategoryViewSet(viewsets.ModelViewSet):
    # The queryset defines the set of objects that will be retrieved by the viewset.
    queryset = Category.objects.all()
    
    # This defines which serializer should be used to serialize and deserialize the data.
    serializer_class = CategorySerializer
    
    # This defines which permissions the user needs to access this view.
    permission_classes = [IsAuthenticated, IsAdmin]

    def create(self, request, *args, **kwargs):
        # Custom response for successful creation
        response = super().create(request, *args, **kwargs)
        return Response(
            {
                "message": "Category created successfully!",
                "data": response.data,
            },
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        # Custom response for successful update
        response = super().update(request, *args, **kwargs)
        return Response(
            {
                "message": "Category updated successfully!",
                "data": response.data,
            },
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        # Custom response for successful deletion
        super().destroy(request, *args, **kwargs)
        return Response(
            {
                "message": "Category deleted successfully!",
            },
            status=status.HTTP_204_NO_CONTENT,
        )

#=========================================================CATEGORY ENTERING END==========================

#=========================================================================================================
#=========================================================================================================

#=========================================================BRAND ENTERING Start==========================

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class  = BrandSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def create(self, request, *args, **kwargs):
        # Custom response for successful creation
        response = super().create(request, *args, **kwargs)
        return Response(
            {
                "message": "Brand created successfully!",
                "data": response.data,
            },
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        # Custom response for successful update
        response = super().update(request, *args, **kwargs)
        return Response(
            {
                "message": "Brand updated successfully!",
                "data": response.data,
            },
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        # Custom response for successful deletion
        super().destroy(request, *args, **kwargs)
        return Response(
            {
                "message": "Brand deleted successfully!",
            },
            status=status.HTTP_204_NO_CONTENT,
        )
    
@swagger_auto_schema(methods=['get'],operation_description="Get a list of all Brands allow for public access")
@api_view(['GET'])
@permission_classes([AllowAny])
def view_brand_allow_any(request):
    brand = Brand.objects.all()
    serializer = BrandSerializer(brand, many = True)
    return Response(serializer.data,status=status.HTTP_200_OK )


@swagger_auto_schema(methods=['get'],operation_description="Get a Single Instance categories for public access")
@api_view(['GET'])
@permission_classes([AllowAny])
def brands_single_view_allow_any(request,pk):
    brand = get_object_or_404(Brand, id = pk)
    serializer = BrandSerializer(instance = brand)
    return Response(serializer.data, status=status.HTTP_200_OK)

#=========================================================BRAND ENTERING END==========================


#=========================================================================================================
#=========================================================================================================
#=========================================================================================================
#=========================================================================================================

#=========================================================Attribute Category ENTERING START==========================
#ProductAttributeCategory 

class ProductAttributeCategorySerializerViewSet(viewsets.ModelViewSet):
    queryset = ProductAttributeCategory.objects.all()
    serializer_class  = ProductAttributeCategorySerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def create(self, request, *args, **kwargs):
        # Custom response for successful creation
        response = super().create(request, *args, **kwargs)
        return Response(
            {
                "message": "Attribute Category created successfully!",
                "data": response.data,
            },
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        # Custom response for successful update
        response = super().update(request, *args, **kwargs)
        return Response(
            {
                "message": "Attribute Category updated successfully!",
                "data": response.data,
            },
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        # Custom response for successful deletion
        super().destroy(request, *args, **kwargs)
        return Response(
            {
                "message": "Attribute Category deleted successfully!",
            },
            status=status.HTTP_204_NO_CONTENT,
        )
    

#=========================================================Attribute Category ENTERING START==========================
# model : ProductAttribute

class ProductAttributeViewSet(viewsets.ModelViewSet):
    queryset = ProductAttribute.objects.all()
    serializer_class = ProductAttributeSerializer
    permission_classes = [IsAuthenticated,IsAdmin]

    def create(self, request, *args, **kwargs):
        # Custom response for successful creation
        response = super().create(request, *args, **kwargs)
        return Response(
            {
                "message": "Attribute  created successfully!",
                "data": response.data,
            },
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        # Custom response for successful update
        response = super().update(request, *args, **kwargs)
        return Response(
            {
                "message": "Attribute  updated successfully!",
                "data": response.data,
            },
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        # Custom response for successful deletion
        super().destroy(request, *args, **kwargs)
        return Response(
            {
                "message": "Attribute deleted successfully!",
            },
            status=status.HTTP_204_NO_CONTENT,
        )

#=========================================================Attribute Category ENTERING END==========================




#=========================================================Attribute Value Start==========================



# model :ProductAttributeValue

class ProductAttributeValueViewSet(viewsets.ModelViewSet):
    queryset = ProductAttributeValue.objects.all()
    serializer_class = ProductAttributeValueSerializer 
    permission_classes = [IsAuthenticated, IsAdmin]

    def create(self, request, *args, **kwargs):
        # Custom response for successful creation
        response = super().create(request, *args, **kwargs)
        input_data = request.data
        product_id = input_data["product_id"]
        product = get_object_or_404(Product, id = product_id)
        product_serializer = ProductSerializer(instance =product) 
        return Response(
            {
                "message": "Product Attribute Value  created successfully!",
                "data": response.data,
                
            },
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        # Custom response for successful update
        response = super().update(request, *args, **kwargs)
        input_data = request.data
        product_id = input_data["product_id"]
        product = get_object_or_404(Product, id = product_id)
        product_serializer = ProductSerializer(instance =product) 
        return Response(
            {
                "message": "Product Attribute Value   updated successfully!",
                "data": response.data,
            },
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        # Custom response for successful deletion
        super().destroy(request, *args, **kwargs)
        return Response(
            {
                "message": "Product Attribute Value  deleted successfully!",
            },
            status=status.HTTP_204_NO_CONTENT,
        )
    
#=========================================================Attribute Value end==========================

#=========================================================Attribute Value  details Start==========================

# model:- AttributeValueDetail 

class AttributeValueDetailViewSet(viewsets.ModelViewSet):
    queryset = AttributeValueDetail.objects.all()
    serializer_class = AttributeValueDetailSerializer

    permission_classes = [IsAuthenticated, IsAdmin]

    def create(self, request, *args, **kwargs):
        # Custom response for successful creation
        response = super().create(request, *args, **kwargs)
        input_data = request.data
        attribute_id = input_data["attribute_value_id"]
        product = get_object_or_404(ProductAttributeValue, id = attribute_id).product
        product_serializer = ProductSerializer(instance =product) 
        return Response(
            {
                "message": "Product Attribute Value Details created successfully!",
                "data": product_serializer.data,
                
            },
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        # Custom response for successful update
        response = super().update(request, *args, **kwargs)
        input_data = request.data
        attribute_id = input_data["attribute_value_id"]
        product = get_object_or_404(ProductAttributeValue, id = attribute_id).product
        product_serializer = ProductSerializer(instance =product) 
        return Response(
            {
                "message": "Product Attribute Value Details   updated successfully!",
                "data": product_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        # Custom response for successful deletion
        super().destroy(request, *args, **kwargs)
        return Response(
            {
                "message": "Product Attribute Value  Details deleted successfully!",
            },
            status=status.HTTP_204_NO_CONTENT,
        )
    
#=========================================================Attribute Value end==========================
#=========================================================================================================
#=========================================================================================================
#=========================================================================================================
#=========================================================================================================
#=========================================================Product Variant START==========================
# modal: VariantRelationshipAttribute

class VariantRelationshipAttributeViewSet(viewsets.ModelViewSet):
    queryset = VariantRelationshipAttribute.objects.all()
    serializer_class = VariantRelationshipAttributeSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


    def create(self, request, *args, **kwargs):
        # Custom response for successful creation
        response = super().create(request, *args, **kwargs)
        
        return Response(
            {
                "message": "Variant Relationship  Value created successfully!",
                "data": response.data,
                
            },
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        # Custom response for successful update
        response = super().update(request, *args, **kwargs)
        
        return Response(
            {
                "message": "Variant Relationship  Value updated successfully!",
                "data": response.data,
            },
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        # Custom response for successful deletion
        super().destroy(request, *args, **kwargs)
        return Response(
            {
                "message": "Variant Relationship  Value  Details deleted successfully!",
            },
            status=status.HTTP_204_NO_CONTENT,
        )

# model: ProductVariant
#    

class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


    def create(self, request, *args, **kwargs):
        # Custom response for successful creation
        response = super().create(request, *args, **kwargs)
        
        return Response(
            {
                "message": "Variant created successfully!",
                "data": response.data,
                
            },
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        # Custom response for successful update
        response = super().update(request, *args, **kwargs)
        
        return Response(
            {
                "message": "Variant updated successfully!",
                "data": response.data,
            },
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        # Custom response for successful deletion
        super().destroy(request, *args, **kwargs)
        return Response(
            {
                "message": "Variant deleted successfully!",
            },
            status=status.HTTP_204_NO_CONTENT,
        )



#=========================================================Product Variant end==========================
#=========================================================================================================
#=========================================================================================================
# =================================================== Creating Products =================================

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated,IsAdmin]

    def create(self, request, *args, **kwargs):
        # Custom response for successful creation
        response = super().create(request, *args, **kwargs)
        
        return Response(
            {
                "message": "Product created successfully!",
                "data": response.data,
                
            },
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        # Custom response for successful update
        response = super().update(request, *args, **kwargs)
        
        return Response(
            {
                "message": "Product updated successfully!",
                "data": response.data,
            },
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        # Custom response for successful deletion
        super().destroy(request, *args, **kwargs)
        return Response(
            {
                "message": "Product deleted successfully!",
            },
            status=status.HTTP_204_NO_CONTENT,
        )


from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser

from django.db import transaction


from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Add these decorators above each method in ProductMediaViewSet

class ProductMediaViewSet(viewsets.ViewSet):
    """
    API endpoints for managing product media (images and videos)
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    parser_classes = [MultiPartParser, FormParser]
    
    @swagger_auto_schema(
        operation_description="Upload one or multiple images to a product",
        manual_parameters=[
            openapi.Parameter(
                name='image',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description='One or multiple image files to upload',
                allow_empty_value=False
            ),
            openapi.Parameter(
                name='is_primary',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_BOOLEAN,
                required=False,
                description='Set as primary product image',
                default=False
            ),
        ],
        responses={
            201: openapi.Response(
                description="Images added successfully",
                examples={
                    "application/json": {
                        "message": "1 image(s) added successfully",
                        "images": [
                            {
                                "id": 1,
                                "image": "product_images/example.jpg",
                                "is_primary": True
                            }
                        ]
                    }
                }
            ),
            400: "No images provided",
            404: "Product not found"
        }
    )
    @action(detail=True, methods=['post'], url_path='add-image')
    def add_image(self, request, pk=None):
        """Add a new image to a product"""
        # Original implementation remains the same
        """
        Add a new image to a product.
        POST /api/products/{product_id}/add-image/
        """
        product = get_object_or_404(Product, pk=pk)
        
        # Handle single or multiple image uploads
        images = request.FILES.getlist('image')
        if not images:
            return Response(
                {"error": "No images provided"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        is_primary = request.data.get('is_primary', False)
        # Convert string 'true'/'false' to boolean if needed
        if isinstance(is_primary, str):
            is_primary = is_primary.lower() == 'true'
            
        created_images = []
        
        with transaction.atomic():
            for img in images:
                image_data = {
                    'product': product,
                    'image': img,
                    'is_primary': is_primary and len(created_images) == 0  # Only first image can be primary
                }
                product_image = ProductImage.objects.create(**image_data)
                serializer = ProductImageSerializer(product_image)
                created_images.append(serializer.data)
                
        return Response(
            {"message": f"{len(created_images)} image(s) added successfully", "images": created_images},
            status=status.HTTP_201_CREATED
        )
    
    @swagger_auto_schema(
        operation_description="Upload one or multiple videos to a product",
        manual_parameters=[
            openapi.Parameter(
                name='video',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description='One or multiple video files to upload',
                allow_empty_value=False
            ),
        ],
        responses={
            201: openapi.Response(
                description="Videos added successfully",
                examples={
                    "application/json": {
                        "message": "1 video(s) added successfully",
                        "videos": [
                            {
                                "id": 1,
                                "video": "product_videos/example.mp4"
                            }
                        ]
                    }
                }
            ),
            400: "No videos provided",
            404: "Product not found"
        }
    )
    @action(detail=True, methods=['post'], url_path='add-video')
    def add_video(self, request, pk=None):
       
        product = get_object_or_404(Product, pk=pk)
        
        # Handle single or multiple video uploads
        videos = request.FILES.getlist('video')
        if not videos:
            return Response(
                {"error": "No videos provided"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        created_videos = []
        
        with transaction.atomic():
            for vid in videos:
                video_data = {
                    'product': product,
                    'video': vid
                }
                product_video = ProductVideo.objects.create(**video_data)
                serializer = ProductVideoSerializer(product_video)
                created_videos.append(serializer.data)
                
        return Response(
            {"message": f"{len(created_videos)} video(s) added successfully", "videos": created_videos},
            status=status.HTTP_201_CREATED
        )
    
    @swagger_auto_schema(
        operation_description="List all images for a product",
        responses={
            200: openapi.Response(
                description="List of product images",
                examples={
                    "application/json": [
                        {
                            "id": 1,
                            "image": "product_images/example1.jpg",
                            "is_primary": True
                        },
                        {
                            "id": 2,
                            "image": "product_images/example2.jpg",
                            "is_primary": False
                        }
                    ]
                }
            ),
            404: "Product not found"
        }
    )
    @action(detail=True, methods=['get'], url_path='images')
    def list_images(self, request, pk=None):
        """
        List all images for a product.
        GET /api/products/{product_id}/images/
        """
        product = get_object_or_404(Product, pk=pk)
        images = ProductImage.objects.filter(product=product)
        serializer = ProductImageSerializer(images, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="List all videos for a product",
        responses={
            200: openapi.Response(
                description="List of product videos",
                examples={
                    "application/json": [
                        {
                            "id": 1,
                            "video": "product_videos/example1.mp4"
                        },
                        {
                            "id": 2,
                            "video": "product_videos/example2.mp4"
                        }
                    ]
                }
            ),
            404: "Product not found"
        }
    )
    @action(detail=True, methods=['get'], url_path='videos')
    def list_videos(self, request, pk=None):
        """
        List all videos for a product.
        GET /api/products/{product_id}/videos/
        """
        product = get_object_or_404(Product, pk=pk)
        videos = ProductVideo.objects.filter(product=product)
        serializer = ProductVideoSerializer(videos, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Set an image as the primary image for a product",
        responses={
            200: openapi.Response(
                description="Primary image updated",
                examples={
                    "application/json": {
                        "message": "Primary image updated successfully"
                    }
                }
            ),
            404: "Product or image not found"
        }
    )
    @action(detail=True, methods=['patch'], url_path='set-primary-image/(?P<image_id>[^/.]+)')
    def set_primary_image(self, request, pk=None, image_id=None):
        """
        Set an image as the primary image for a product.
        PATCH /api/products/{product_id}/set-primary-image/{image_id}/
        """
        product = get_object_or_404(Product, pk=pk)
        image = get_object_or_404(ProductImage, pk=image_id, product=product)
        
        # The model's save method will handle updating other images
        image.is_primary = True
        image.save()
        
        return Response(
            {"message": "Primary image updated successfully"},
            status=status.HTTP_200_OK
        )
    
    @swagger_auto_schema(
        operation_description="Delete an image from a product. If it was the primary image, another one will be set as primary if available.",
        responses={
            200: openapi.Response(
                description="Image deleted",
                examples={
                    "application/json": {
                        "message": "Image deleted successfully"
                    }
                }
            ),
            404: "Product or image not found"
        }
    )
    @action(detail=True, methods=['delete'], url_path='delete-image/(?P<image_id>[^/.]+)')
    def delete_image(self, request, pk=None, image_id=None):
        """
        Delete an image from a product.
        DELETE /api/products/{product_id}/delete-image/{image_id}/
        """
        product = get_object_or_404(Product, pk=pk)
        image = get_object_or_404(ProductImage, pk=image_id, product=product)
        
        # Store if it was a primary image
        was_primary = image.is_primary
        
        # Delete the image
        image.delete()
        
        # If we deleted a primary image, set another one as primary if any exist
        if was_primary:
            remaining_images = ProductImage.objects.filter(product=product).first()
            if remaining_images:
                remaining_images.is_primary = True
                remaining_images.save()
        
        return Response(
            {"message": "Image deleted successfully"},
            status=status.HTTP_200_OK
        )
    
    @swagger_auto_schema(
        operation_description="Delete a video from a product",
        responses={
            200: openapi.Response(
                description="Video deleted",
                examples={
                    "application/json": {
                        "message": "Video deleted successfully"
                    }
                }
            ),
            404: "Product or video not found"
        }
    )
    @action(detail=True, methods=['delete'], url_path='delete-video/(?P<video_id>[^/.]+)')
    def delete_video(self, request, pk=None, video_id=None):
        """
        Delete a video from a product.
        DELETE /api/products/{product_id}/delete-video/{video_id}/
        """
        product = get_object_or_404(Product, pk=pk)
        video = get_object_or_404(ProductVideo, pk=video_id, product=product)
        
        # Delete the video
        video.delete()
        
        return Response(
            {"message": "Video deleted successfully"},
            status=status.HTTP_200_OK
        )
        
    @swagger_auto_schema(
        operation_description="Upload multiple images and videos at once",
        manual_parameters=[
            openapi.Parameter(
                name='images',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=False,
                description='Multiple image files to upload',
                allow_empty_value=True
            ),
            openapi.Parameter(
                name='videos',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=False,
                description='Multiple video files to upload',
                allow_empty_value=True
            ),
            openapi.Parameter(
                name='primary_image_index',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_INTEGER,
                required=False,
                description='Index of the image to set as primary (0-based)',
                default=0
            ),
        ],
        responses={
            201: openapi.Response(
                description="Media files added successfully",
                examples={
                    "application/json": {
                        "message": "Added 2 image(s) and 1 video(s) successfully",
                        "images": [
                            {
                                "id": 1,
                                "image": "product_images/example1.jpg",
                                "image_url": "http://example.com/media/product_images/example1.jpg",
                                "is_primary": True
                            },
                            {
                                "id": 2,
                                "image": "product_images/example2.jpg",
                                "image_url": "http://example.com/media/product_images/example2.jpg",
                                "is_primary": False
                            }
                        ],
                        "videos": [
                            {
                                "id": 1,
                                "video": "product_videos/example.mp4",
                                "video_url": "http://example.com/media/product_videos/example.mp4"
                            }
                        ]
                    }
                }
            ),
            400: "No media files provided",
            404: "Product not found"
        }
    )
    @action(detail=True, methods=['post'], url_path='bulk-upload')
    def bulk_upload(self, request, pk=None):
        """
        Upload multiple images and videos at once
        POST /api/products/{product_id}/bulk-upload/
        """
        product = get_object_or_404(Product, pk=pk)
        
        images = request.FILES.getlist('images')
        videos = request.FILES.getlist('videos')
        primary_image_index = int(request.data.get('primary_image_index', 0))
        
        if not images and not videos:
            return Response(
                {"error": "No media files provided"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # Process images
            created_images = []
            for i, img in enumerate(images):
                image_data = {
                    'product': product,
                    'image': img,
                    'is_primary': i == primary_image_index
                }
                product_image = ProductImage.objects.create(**image_data)
                serializer = ProductImageSerializer(product_image, context={'request': request})
                created_images.append(serializer.data)
            
            # Process videos
            created_videos = []
            for vid in videos:
                video_data = {
                    'product': product,
                    'video': vid
                }
                product_video = ProductVideo.objects.create(**video_data)
                serializer = ProductVideoSerializer(product_video, context={'request': request})
                created_videos.append(serializer.data)
        
        return Response({
            "message": f"Added {len(created_images)} image(s) and {len(created_videos)} video(s) successfully",
            "images": created_images,
            "videos": created_videos
        }, status=status.HTTP_201_CREATED)




# =================================================== Creating Products =================================


#=========================================================================================================
#=========================================================================================================
# ===================================================  Products Pairing =================================


from .models import Product, ProductPairing
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import (
    ProductPairingSerializer, 
    ProductPairingCreateSerializer,
    ProductWithPairingsSerializer
)

class ProductPairingViewSet(viewsets.ModelViewSet):
    """ViewSet for CRUD operations on product pairings"""
    queryset = ProductPairing.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['primary_product', 'paired_product', 'is_active', 'pairing_strength']
    search_fields = ['primary_product__name', 'paired_product__name', 'description']
    ordering_fields = ['pairing_strength', 'created_at']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProductPairingCreateSerializer
        return ProductPairingSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [AllowAny()]
    
    @action(detail=False, methods=['get'])
    def for_product(self, request):
        """Get all pairings for a specific product"""
        product_id = request.query_params.get('product_id')
        if not product_id:
            return Response(
                {"error": "product_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )
            
        pairings = ProductPairing.objects.filter(
            primary_product=product,
            is_active=True
        )
        serializer = ProductPairingSerializer(pairings, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle the is_active status of a product pairing"""
        pairing = self.get_object()
        pairing.is_active = not pairing.is_active
        pairing.save()
        return Response({
            "status": "success",
            "is_active": pairing.is_active
        })

class ProductWithPairingsView(generics.RetrieveAPIView):
    """View to get a product with its paired products"""
    queryset = Product.objects.all()
    serializer_class = ProductWithPairingsSerializer
    permission_classes = [AllowAny]
    
    def get_object(self):
        # Allow lookup by product_code or primary key
        lookup_field = self.kwargs.get('pk')
        
        # First try to find by product_code
        product = Product.objects.filter(product_code=lookup_field).first()
        if not product:
            # If not found, try to find by primary key
            try:
                product = Product.objects.get(pk=lookup_field)
            except Product.DoesNotExist:
                pass
                
        if not product:
            self.permission_denied(self.request)
            
        return product
    
    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        Ensures the request is passed to nested serializers.
        """
        context = super().get_serializer_context()
        return context
    

#product recommendation system 




from .models import Product, ProductRecommendation, ProductView
from .serializers import (
    ProductLightSerializer,
    ProductRecommendationSerializer,
    RecommendationResultSerializer
)
from .recommendation_service import RecommendationService

class ProductRecommendationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing product recommendations"""
    queryset = ProductRecommendation.objects.all()
    serializer_class = ProductRecommendationSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'refresh_recommendations']:
            return [IsAdmin]
        return [AllowAny()]
        
    @action(detail=False, methods=['get'])
    def by_product(self, request):
        """Get recommendations for a specific product, optionally filtered by type"""
        product_id = request.query_params.get('product_id')
        rec_type = request.query_params.get('type')
        limit = int(request.query_params.get('limit', 5))
        
        if not product_id:
            return Response(
                {"error": "product_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )
            
        # Record this product view if user or session is provided
        user = request.user if request.user.is_authenticated else None
        session_id = request.session.session_key if hasattr(request, 'session') else None
        
        if user or session_id:
            ProductView.record_view(product, user=user, session_id=session_id)
            
        # Get recommendations based on type
        if rec_type:
            recommendations = RecommendationService.get_recommendations(
                product, 
                recommendation_type=rec_type,
                limit=limit
            )
            serializer = ProductLightSerializer(recommendations, many=True)
            return Response(serializer.data)
        else:
            # Get all recommendation types
            recommendations = RecommendationService.get_all_recommendations(
                product,
                limit_per_type=limit
            )
            
            # Add recently viewed if available
            if user or session_id:
                recently_viewed = ProductView.get_recently_viewed(
                    user=user, 
                    session_id=session_id,
                    limit=limit
                )
                # Filter out the current product
                recently_viewed = [p for p in recently_viewed if p.id != product.id]
                if recently_viewed:
                    recommendations['recently_viewed'] = recently_viewed
            
            serializer = RecommendationResultSerializer(recommendations)
            return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Get trending products"""
        limit = int(request.query_params.get('limit', 10))
        
        # Get products marked as trending
        trending_recs = ProductRecommendation.objects.filter(
            recommendation_type='trending',
            is_active=True,
            recommended_product__is_available=True
        ).order_by('-score')[:limit]
        
        trending_products = [rec.recommended_product for rec in trending_recs]
        serializer = ProductLightSerializer(trending_products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def refresh_recommendations(self, request):
        """Refresh recommendations for a product or all products"""
        product_id = request.data.get('product_id')
        
        if product_id:
            try:
                product = Product.objects.get(id=product_id)
                RecommendationService.refresh_all_recommendations(product)
                return Response({
                    "status": "success",
                    "message": f"Recommendations refreshed for product {product.name}"
                })
            except Product.DoesNotExist:
                return Response(
                    {"error": "Product not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # This can be a long-running process, so in a real application
            # you might want to use a background task or Celery
            transaction.on_commit(
                lambda: RecommendationService.refresh_all_recommendations()
            )
            return Response({
                "status": "success",
                "message": "Recommendation refresh scheduled for all products"
            })
    
    @action(detail=False, methods=['get'])
    def recently_viewed(self, request):
        """Get recently viewed products for the current user/session"""
        limit = int(request.query_params.get('limit', 10))
        
        user = request.user if request.user.is_authenticated else None
        session_id = request.session.session_key if hasattr(request, 'session') else None
        
        if not (user or session_id):
            return Response(
                {"error": "Authentication or session required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        recently_viewed = ProductView.get_recently_viewed(
            user=user, 
            session_id=session_id,
            limit=limit
        )
        
        serializer = ProductLightSerializer(recently_viewed, many=True)
        return Response(serializer.data)