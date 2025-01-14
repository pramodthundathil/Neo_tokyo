from django.shortcuts import render, redirect, get_object_or_404
import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
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

    CategorySerializer

)
from .models import Product, Category, Tax, ProductImage, ProductVideo
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




# product views serializers can get the response of all product details and single details 
# it will allow all users to access this data even guest user 
# example Api JSON data is below
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tax_view(request):
    tax = Tax.objects.all()
    serializer = TaxSerializer(tax, many = True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tax_single_view(request,pk):
    tax = get_object_or_404(Tax, id = pk)
    serializer = TaxSerializer(instance = tax)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
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



#=========================================================TAX DATA ENTERING START========================




#=========================================================TAX DATA ENTERING END==========================





#=========================================================================================================
#=========================================================================================================
#=========================================================================================================
#=========================================================================================================