# Generated by Django 5.1.4 on 2025-05-05 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interactions', '0004_grievanceticket_product_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='grievanceticket',
            name='image',
            field=models.FileField(blank=True, null=True, upload_to='grievance_image'),
        ),
        migrations.AddField(
            model_name='grievanceticket',
            name='link',
            field=models.URLField(blank=True, null=True),
        ),
    ]
