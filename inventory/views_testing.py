from django import forms
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Tax, Category, Brand, Product, ProductImage, ProductVideo
from .forms import (
    TaxForm,
    CategoryForm,
    BrandForm,
    ProductForm,
    ProductImageForm,
    ProductVideoForm,

)

# Admin Board View
@login_required(login_url='signin')
def admin_board(request):
    tax_form = TaxForm()
    category_form = CategoryForm()
    brand_form = BrandForm()
    product_form = ProductForm()
    product_image_form = ProductImageForm()
    product_video_form = ProductVideoForm()


    context = {
        "tax_form": tax_form,
        "category_form": category_form,
        "brand_form": brand_form,
        "product_form": product_form,
        "product_image_form": product_image_form,
        "product_video_form": product_video_form,
    
    }
    return render(request, "index.html", context)

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



def product_view(request):
    products = Product.objects.all()

    context = {
        "products":products
    }
    return render(request,"product_view.html",context)



# tax fields 

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Tax
from .forms import TaxForm

@login_required(login_url='signin')
def AddTax(request):
    if request.method == "POST":
        name = request.POST.get('name')
        tax_rate = request.POST.get('tax')
        tax = Tax.objects.create(tax_name = name,tax_percentage = tax_rate )
        tax.save()
        messages.success(request,'Tax Value Added Success')
        return redirect("ListTax")
    return render(request,"add-tax-slab.html")


@login_required(login_url='signin')
def ListTax(request):
    tax = Tax.objects.all()
    context = {
        "tax":tax
    }
    return render(request,"list-tax.html",context)


@login_required(login_url='signin')
def delete_tax(request,pk):
    tax = get_object_or_404(Tax,pk=pk)
    tax.delete()
    messages.success(request,'Tax Value Deleted Success')
    return redirect("ListTax")


@login_required(login_url='signin')
def tax_single_update(request,pk):
    tax = get_object_or_404(Tax,pk=pk)
    form = TaxForm(instance = tax)
    if request.method == "POST":
        form = TaxForm(request.POST,instance = tax)
        if form.is_valid():
            tax = form.save()
            tax.save()
            messages.success(request,'Tax Value Updated Success')
            return redirect("ListTax")
    return render(request,"tax-single.html",{"form":form})


@login_required(login_url='signin')
def list_products(request):
    products = Product.objects.all()

    context = {
        "products":products
    }
    return render(request,"list-products.html",context)


from .forms import ProductAttributeCategoryForm, ProductAttributeValueForm, ProductAttributeForm, AttributeValueDetailForm
from .models import ProductAttributeCategory, ProductAttributeValue, AttributeValueDetail
from collections import defaultdict

@login_required(login_url='signin')
def add_category(request):
    form1 = ProductAttributeCategoryForm()
    form2 = ProductAttributeForm()
    categories = ProductAttributeCategory.objects.all()

    if request.method == "POST":
        if "items" in request.POST:  # Identify which form was submitted
            form1 = ProductAttributeCategoryForm(request.POST)  # Handle file uploads for ProductForm
            if form1.is_valid():
                form1.save()
                messages.success(request, "Category saved successfully!")
                return redirect("add_category")
            else:
                messages.error(request, f"Failed to save Category. Please fix the errors.{form1.errors}")
                return redirect("add_category")

        
        elif "cat" in request.POST:
            form2 = ProductAttributeForm(request.POST)
            if form2.is_valid():
                form2.save()
                messages.success(request, "Category Attribute saved successfully!")
                return redirect("add_category")
            else:
                messages.error(request, f"Failed to save category Attribute. Please fix the errors.{form2.errors}")
                return redirect("add_category") 

    context = {
        "form1":form1,
        "form2":form2,
        "categories":categories
    }
    return render(request,"category-add.html",context)


@login_required(login_url='signin')
def add_product(request):
    form = ProductForm()
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            product.save()
            messages.success(request,"Product added Successfully Please update other values  ")
            return redirect("product_update",pk = product.id )
        else:
            messages.success(request,"Something wrong!!!!!!! ")
            return redirect(add_product)

    context = {
        "form":form
    }
    return render(request,"add-products.html",context)


@login_required(login_url='signin')
def product_update(request, pk):
    product = get_object_or_404(Product, id=pk)
    form = ProductForm(instance=product)
    form1 = ProductImageForm(initial={'product': product})
    form2 = ProductVideoForm(initial={'product': product})
    form3 = ProductAttributeValueForm(initial={'product': product})
    

    if request.method == "POST":
        if "photo" in request.POST:
            form1 = ProductImageForm(request.POST, request.FILES)
            if form1.is_valid():
                photo = form1.save(commit=False)
                photo.product = product
                photo.save()
                messages.success(request, "Photo saved successfully!")
            else:
                messages.error(request, "Failed to save photo. Please fix the errors.")
            return redirect("product_update", pk=pk)

        elif "video" in request.POST:
            form2 = ProductVideoForm(request.POST, request.FILES)
            if form2.is_valid():
                video = form2.save(commit=False)
                video.product = product
                video.save()
                messages.success(request, "Video saved successfully!")
            else:
                messages.error(request, "Failed to save video. Please fix the errors.")
            return redirect("product_update", pk=pk)

        elif "product" in request.POST:
            form = ProductAttributeValueForm(request.POST)
            if form.is_valid():
                overview = form.save()
                overview.product = product
                overview.save()
                messages.success(request, "Overview added successfully!")
            else:
                messages.error(request, "Failed to update Overview. Please fix the errors.")
            return redirect("product_update", pk=pk)
        

        elif "overview" in request.POST:
            form = ProductForm(request.POST, request.FILES, instance=product)
            if form.is_valid():
                form.save()
                messages.success(request, "Product updated successfully!")
            else:
                messages.error(request, "Failed to update product. Please fix the errors.")
            return redirect("product_update", pk=pk)

    attributes_grouped = defaultdict(list)

    for attribute_value in product.attributes.all():
        attributes_grouped[attribute_value.attribute.category].append(attribute_value)

    context = {"form": form, "form1": form1, "form2": form2,"form3":form3, "product":product,"attributes_grouped":attributes_grouped}
    return render(request, "product_update.html", context)


@login_required(login_url='signin')
def add_attribute_value_to_product(request,pk):
    attribute = get_object_or_404(ProductAttributeValue, id = pk)
    if request.method == "POST":
        val = request.POST.get("val")
        details = AttributeValueDetail.objects.create(attribute_value =attribute,value = val  )
        details.save()
        messages.success(request, "Attribute value added...")
        return redirect(product_update,pk = attribute.product.id )
    
from django.db.models import F
from itertools import groupby

@login_required(login_url='signin')
def View_product(request,pk):
    product = get_object_or_404(Product,id= pk)
    # Annotate and sort by category
   # Fetch and sort attributes by category
    attributes = product.attributes.select_related('attribute').prefetch_related('details').order_by('attribute__category')

    # Group attributes by category
    grouped_attributes = {}
    for key, group in groupby(attributes, key=lambda x: x.attribute.category):
        grouped_attributes[key] = list(group)

    context = {"product":product,"grouped_attributes": grouped_attributes}
    return render(request,"view_product_single.html",context)


def list_brand(request):
    form1 = BrandForm()
    form2 = CategoryForm()
    category = Category.objects.all()
    brand = Brand.objects.all()
    if request.method == "POST":
        if "brand" in request.POST:
            form1 = BrandForm(request.POST)
            if form1.is_valid():
                form1.save()
                
                messages.success(request, "Brand saved successfully!")
            else:
                messages.error(request, f"Failed to save Brand. Please fix the errors.{form1.errors}")
            return redirect(list_brand)

        elif "category" in request.POST:
            form2 = CategoryForm(request.POST)
            if form2.is_valid():
                form2.save()
                messages.success(request, "Category saved successfully!")
            else:
                messages.error(request, "Failed to save Category. Please fix the errors.")
            return redirect(list_brand)


    context = {
        "form1":form1,
        "form2":form2,
        "category":category,
        "brand":brand
    }
    return render(request,"list-brand.html",context)