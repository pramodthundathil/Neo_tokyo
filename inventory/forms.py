from django import forms
from .models import Tax, Category, Brand, Product, ProductImage, ProductVideo, Attribute, ProductSpecification, ProductVariant

# Tax Form
class TaxForm(forms.ModelForm):
    class Meta:
        model = Tax
        fields = '__all__'
        widgets = {
            'tax_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'tax_name',"placeholder":"Tax Name"}),
            'tax_percentage': forms.NumberInput(attrs={'class': 'form-control', 'id': 'tax_percentage',"placeholder":"Tax percentage"}),
        }

# Category Form
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'id': 'category_name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'id': 'category_description'}),
            'parent': forms.Select(attrs={'class': 'form-control', 'id': 'category_parent'}),
        }

# Brand Form
class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'id': 'brand_name'}),
        }

# Product Form
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'product_code': forms.TextInput(attrs={'class': 'form-control', 'id': 'product_code'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'id': 'product_name'}),
            'brand': forms.Select(attrs={'class': 'form-control', 'id': 'product_brand'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'id': 'product_description'}),
            'category': forms.Select(attrs={'class': 'form-control', 'id': 'product_category'}),
            'mrp': forms.NumberInput(attrs={'class': 'form-control', 'id': 'product_mrp'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'id': 'product_price'}),
            'discount_price': forms.NumberInput(attrs={'class': 'form-control', 'id': 'product_discount_price'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'id': 'product_stock'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'product_is_available'}),
            'youtube_url': forms.URLInput(attrs={'class': 'form-control', 'id': 'product_youtube_url'}),
            'broacher': forms.FileInput(attrs={'class': 'form-control', 'id': 'product_broacher'}),
            'tax': forms.Select(attrs={'class': 'form-control', 'id': 'product_tax'}),
            'tax_value': forms.Select(attrs={'class': 'form-control', 'id': 'product_tax_value'}),
        }

# Product Image Form
class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = '__all__'
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control', 'id': 'product_image_product'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'id': 'product_image_file'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'product_image_is_primary'}),
        }

# Product Video Form
class ProductVideoForm(forms.ModelForm):
    class Meta:
        model = ProductVideo
        fields = '__all__'
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control', 'id': 'product_video_product'}),
            'video': forms.FileInput(attrs={'class': 'form-control', 'id': 'product_video_file'}),
        }

# Attribute Form
class AttributeForm(forms.ModelForm):
    class Meta:
        model = Attribute
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'id': 'attribute_name'}),
            'value': forms.TextInput(attrs={'class': 'form-control', 'id': 'attribute_value'}),
        }

# Product Specification Form
class ProductSpecificationForm(forms.ModelForm):
    class Meta:
        model = ProductSpecification
        fields = '__all__'
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control', 'id': 'specification_product'}),
            'attributes': forms.SelectMultiple(attrs={'class': 'form-control', 'id': 'specification_attributes'}),
        }

# Product Variant Form
class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = '__all__'
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control', 'id': 'variant_product'}),
            'attributes': forms.SelectMultiple(attrs={'class': 'form-control', 'id': 'variant_attributes'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'id': 'variant_stock'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'id': 'variant_price'}),
        }
