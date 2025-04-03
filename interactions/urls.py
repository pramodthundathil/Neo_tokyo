from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter



urlpatterns = [

    #review and rating urls

    path('products/<int:pk>/reviews/', views.ProductReviewsView.as_view(), name='product-reviews'),
    path("product/<int:pk>/review-view",views.ProductReviewsView.as_view(),name="product-review-view"),
    path('reviews/add/', views.add_product_review, name='add-review'),
    path('reviews/<int:review_id>/update/', views.update_product_review, name='update-review'),
    path('reviews/<int:review_id>/delete/', views.delete_product_review, name='delete-review'),
    path('user/reviews/', views.get_user_reviews, name='user-reviews'),
    path('product/reviews/', views.get_product_reviews, name='get-product-reviews'),

    # ticket handling urls
    path('tickets/<str:ticket_id>/conclude/', views.ConcludeTicketView.as_view(), name='conclude-ticket'),
    path('tickets/<int:pk>/reopen/', views.UserTicketViewSet.as_view({'post': 'reopen'}), name='reopen-ticket'),
    path('admin/tickets/<int:pk>/reopen/', views.AdminTicketViewSet.as_view({'post': 'reopen'}), name='reopen-ticket-admin'),
]


router = DefaultRouter()
router.register(r'my-tickets', views.UserTicketViewSet, basename='user-tickets')
router.register(r'admin/tickets', views.AdminTicketViewSet, basename='admin-tickets')

urlpatterns += router.urls