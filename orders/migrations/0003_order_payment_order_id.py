# Generated by Django 5.1.4 on 2025-02-18 04:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_order_orderitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_order_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
