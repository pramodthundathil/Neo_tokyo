from django.urls import path
from . import views



urlpatterns = [

    path('products/<int:pk>/reviews/', views.ProductReviewsView.as_view(), name='product-reviews'),
    path("product/<int:pk>/review-view",views.ProductReviewsView.as_view(),name="product-review-view"),
    path('reviews/add/', views.add_product_review, name='add-review'),
    path('reviews/<int:review_id>/update/', views.update_product_review, name='update-review'),
    path('reviews/<int:review_id>/delete/', views.delete_product_review, name='delete-review'),
    path('user/reviews/', views.get_user_reviews, name='user-reviews'),
    path('product/reviews/', views.get_product_reviews, name='get-product-reviews'),
]