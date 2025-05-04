import re
from django.conf import settings

class ProductViewMiddleware:
    """Middleware to ensure sessions are created for anonymous users for tracking product views"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Product URL pattern - adjust according to your URL structure
        self.product_url_pattern = re.compile(r'^/api/products/(?P<product_id>\d+|[\w-]+)/?$')
        
    def __call__(self, request):
        # Create session for anonymous users on product pages
        path = request.path_info
        match = self.product_url_pattern.match(path)
        
        if match and request.method == 'GET' and not request.user.is_authenticated:
            # Make sure the user has a session
            if not request.session.session_key:
                request.session.save()
                
        response = self.get_response(request)
        return response