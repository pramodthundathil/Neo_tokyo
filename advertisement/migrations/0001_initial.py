# Generated by Django 5.0.6 on 2025-06-18 10:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('inventory', '0016_product_warranty_info'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductDropDownCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('slug', models.SlugField(blank=True, max_length=60, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('date_added', models.DateField(auto_now_add=True)),
                ('date_modified', models.DateField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Product Category',
                'verbose_name_plural': 'Product Categories',
                'ordering': ['order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='HeroCarousel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.FileField(upload_to='carousel_images/')),
                ('alt_text', models.CharField(blank=True, max_length=100)),
                ('head_one', models.CharField(max_length=50)),
                ('head_two', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=200)),
                ('button_text', models.CharField(default='Shop Now', max_length=20)),
                ('button_link', models.URLField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('date_added', models.DateField(auto_now_add=True)),
                ('date_modified', models.DateField(auto_now=True)),
                ('dropdown_menu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hero_carousels', to='advertisement.productdropdowncategory')),
            ],
            options={
                'verbose_name': 'Hero Carousel',
                'verbose_name_plural': 'Hero Carousels',
                'ordering': ['order', '-date_added'],
            },
        ),
        migrations.CreateModel(
            name='ProductSpecificationDescription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('order', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('date_added', models.DateField(auto_now_add=True)),
                ('date_modified', models.DateField(auto_now=True)),
                ('dropdown_menu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='specifications', to='advertisement.productdropdowncategory')),
            ],
            options={
                'verbose_name': 'Product Specification',
                'verbose_name_plural': 'Product Specifications',
                'ordering': ['order', 'title'],
            },
        ),
        migrations.CreateModel(
            name='ProductListOnProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_featured', models.BooleanField(default=False)),
                ('order', models.PositiveIntegerField(default=0)),
                ('date_added', models.DateField(auto_now_add=True)),
                ('dropdown_menu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='category_products', to='advertisement.productdropdowncategory')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_categories', to='inventory.product')),
            ],
            options={
                'verbose_name': 'Category Product',
                'verbose_name_plural': 'Category Products',
                'ordering': ['order', '-date_added'],
                'unique_together': {('dropdown_menu', 'product')},
            },
        ),
    ]
