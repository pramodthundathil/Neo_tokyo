# Generated by Django 5.1.4 on 2024-12-10 04:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='village',
            new_name='age',
        ),
    ]
