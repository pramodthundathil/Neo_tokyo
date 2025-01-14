from django import forms
from .models import Tax, Category, Brand, Product, ProductImage, ProductVideo

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
            # 'parent': forms.Select(attrs={'class': 'form-control', 'id': 'category_parent'}),
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
        exclude = ["product_code","price_before_tax","tax_amount"]
        widgets = {
            
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
            "more_info":forms.URLInput(attrs={'class': 'form-control', 'id': 'product_youtube_url',"placeholder":"Url for More Information"}),
        }

# Product Image Form
class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        exclude = ["product"]
        widgets = {
            
            'image': forms.FileInput(attrs={'class': 'form-control', 'id': 'product_image_file'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'product_image_is_primary'}),
        }

# Product Video Form
class ProductVideoForm(forms.ModelForm):
    class Meta:
        model = ProductVideo
        exclude = ["product"]

        widgets = {
            'video': forms.FileInput(attrs={'class': 'form-control', 'id': 'product_video_file'}),
        }



# new Forms 

from django import forms
from .models import (
    ProductAttributeCategory,
    ProductAttribute,
    ProductAttributeValue,
    AttributeValueDetail
)

class ProductAttributeCategoryForm(forms.ModelForm):
    class Meta:
        model = ProductAttributeCategory
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter category name'})
        }

class ProductAttributeForm(forms.ModelForm):
    class Meta:
        model = ProductAttribute
        fields = ['category', 'name']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter attribute name'})
        }

class ProductAttributeValueForm(forms.ModelForm):
    class Meta:
        model = ProductAttributeValue
        fields = ['product', 'attribute']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'attribute': forms.Select(attrs={'class': 'form-control'}),
        }

class AttributeValueDetailForm(forms.ModelForm):
    class Meta:
        model = AttributeValueDetail
        fields = ['attribute_value', 'value']
        widgets = {
            'attribute_value': forms.Select(attrs={'class': 'form-control'}),
            'value': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter value'})
        }


from .models import ProductVariant

class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = '__all__'
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'variant_product': forms.Select(attrs={'class': 'form-control'}),
            'relationship': forms.Select(attrs={'class': 'form-control'}),
            'relationship_value': forms.TextInput(attrs={'class': 'form-control'}),
        }