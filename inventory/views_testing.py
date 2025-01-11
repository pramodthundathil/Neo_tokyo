from django import forms
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Tax, Category, Brand, Product, ProductImage, ProductVideo, Attribute, ProductSpecification, ProductVariant
from .forms import (
    TaxForm,
    CategoryForm,
    BrandForm,
    ProductForm,
    ProductImageForm,
    ProductVideoForm,
    AttributeForm,
    ProductSpecificationForm,
    ProductVariantForm,
)

# Admin Board View
def admin_board(request):
    tax_form = TaxForm()
    category_form = CategoryForm()
    brand_form = BrandForm()
    product_form = ProductForm()
    product_image_form = ProductImageForm()
    product_video_form = ProductVideoForm()
    product_attribute_form = AttributeForm()
    product_spec_form = ProductSpecificationForm()
    product_variant_form = ProductVariantForm()

    context = {
        "tax_form": tax_form,
        "category_form": category_form,
        "brand_form": brand_form,
        "product_form": product_form,
        "product_image_form": product_image_form,
        "product_video_form": product_video_form,
        "product_attribute_form": product_attribute_form,
        "product_spec_form": product_spec_form,
        "product_variant_form": product_variant_form,
    }
    return render(request, "admin_user_dash.html", context)

# Tax Add View
def tax_add(request):
    if request.method == "POST":
        form = TaxForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "TAX ADDED")
            return redirect("admin_board")
        else:
            messages.error(request, form.errors)
            return redirect("admin_board")

# Category Add View
def category_add(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category ADDED")
            return redirect("admin_board")
        else:
            messages.error(request, form.errors)
            return redirect("admin_board")

# Brand Add View
def brand_add(request):
    if request.method == "POST":
        form = BrandForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Brand ADDED")
            return redirect("admin_board")
        else:
            messages.error(request, form.errors)
            return redirect("admin_board")

# Product Add View
def product_add(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product ADDED")
            return redirect("admin_board")
        else:
            messages.error(request, form.errors)
            return redirect("admin_board")

# Product Image Add View
def product_image_add(request):
    if request.method == "POST":
        form = ProductImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product Image ADDED")
            return redirect("admin_board")
        else:
            messages.error(request, form.errors)
            return redirect("admin_board")

# Product Video Add View
def product_video_add(request):
    if request.method == "POST":
        form = ProductVideoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product Video ADDED")
            return redirect("admin_board")
        else:
            messages.error(request, form.errors)
            return redirect("admin_board")

# Attribute Add View
def attribute_add(request):
    if request.method == "POST":
        form = AttributeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Attribute ADDED")
            return redirect("admin_board")
        else:
            messages.error(request, form.errors)
            return redirect("admin_board")

# Product Specification Add View
def product_spec_add(request):
    if request.method == "POST":
        form = ProductSpecificationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Product Specification ADDED")
            return redirect("admin_board")
        else:
            messages.error(request, form.errors)
            return redirect("admin_board")

# Product Variant Add View
def product_variant_add(request):
    if request.method == "POST":
        form = ProductVariantForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Product Variant ADDED")
            return redirect("admin_board")
        else:
            messages.error(request, form.errors)
            return redirect("admin_board")
        

def product_view(request):
    products = Product.objects.all()

    context = {
        "products":products
    }
    return render(request,"product_view.html",context)
