# Generated by Django 5.1.4 on 2025-01-16 05:56

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0009_alter_category_name'),
        ('orders', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_number', models.CharField(max_length=20, unique=True)),
                ('total_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('total_tax', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('price_before_tax', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('total_discount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('bill_discount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('product_discount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('payment_status', models.CharField(choices=[('SUCCESS', 'Success'), ('FAILED', 'Failed'), ('PENDING', 'Pending')], default='PENDING', max_length=20)),
                ('order_status', models.CharField(choices=[('PENDING', 'Pending'), ('PAID', 'Paid'), ('FAILED', 'Failed')], default='PENDING', max_length=20)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('product_discount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_tax', models.DecimalField(decimal_places=2, max_digits=10)),
                ('price_after_tax', models.DecimalField(decimal_places=2, max_digits=10)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='orders.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.product')),
            ],
        ),
    ]
