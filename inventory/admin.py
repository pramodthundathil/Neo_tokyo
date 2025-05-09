from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages

from .models import ProductPairing, ProductRecommendation, ProductView

admin.site.register(ProductPairing)
admin.site.register(ProductRecommendation)
admin.site.register(ProductView)

    
    